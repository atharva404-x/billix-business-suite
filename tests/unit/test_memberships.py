import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.base import Base
from app.models.user import User
from app.models.business import Business
from app.models.membership import Membership
from app.models.roles import UserRole
from app.schemas.membership import MemberAdd
from app.services.membership import MembershipService
from app.auth.dependencies import get_current_user
from app.core.database import get_db


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture(autouse=True)
def cleanup_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ==============================================================================
# 1. MembershipService Direct Operations Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_service_add_member_success(async_db):
    owner = User(clerk_id="usr_owner", email="owner@test.com")
    new_user = User(clerk_id="usr_new", email="new@test.com")
    business = Business(business_name="Acme Corporation")

    async_db.add_all([owner, new_user, business])
    await async_db.commit()

    # Owner membership
    m1 = Membership(user_id=owner.id, business_id=business.id, role=UserRole.OWNER)
    async_db.add(m1)
    await async_db.commit()

    service = MembershipService()

    # Add member successfully
    membership = await service.add_member(async_db, owner, business.id, "new@test.com", UserRole.STAFF)
    assert membership.user_id == new_user.id
    assert membership.role == UserRole.STAFF
    assert membership.invited_by == owner.id


@pytest.mark.asyncio
async def test_service_add_member_failures(async_db):
    owner = User(clerk_id="usr_owner", email="owner@test.com")
    staff = User(clerk_id="usr_staff", email="staff@test.com")
    business = Business(business_name="Acme Corporation")

    async_db.add_all([owner, staff, business])
    await async_db.commit()

    # Owner and Staff memberships
    m1 = Membership(user_id=owner.id, business_id=business.id, role=UserRole.OWNER)
    m2 = Membership(user_id=staff.id, business_id=business.id, role=UserRole.STAFF)
    async_db.add_all([m1, m2])
    await async_db.commit()

    service = MembershipService()

    # 1. Staff tries to add member (raises 403)
    with pytest.raises(HTTPException) as exc:
        await service.add_member(async_db, staff, business.id, "random@test.com", UserRole.VIEWER)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    # 2. Try to add non-registered user (raises 400)
    with pytest.raises(HTTPException) as exc:
        await service.add_member(async_db, owner, business.id, "unregistered@test.com", UserRole.VIEWER)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

    # 3. Try to add already existing member (raises 409)
    with pytest.raises(HTTPException) as exc:
        await service.add_member(async_db, owner, business.id, "staff@test.com", UserRole.STAFF)
    assert exc.value.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_service_remove_member_success(async_db):
    owner = User(clerk_id="usr_owner", email="owner@test.com")
    staff = User(clerk_id="usr_staff", email="staff@test.com")
    business = Business(business_name="Acme Corporation")

    async_db.add_all([owner, staff, business])
    await async_db.commit()

    # Memberships
    m1 = Membership(user_id=owner.id, business_id=business.id, role=UserRole.OWNER)
    m2 = Membership(user_id=staff.id, business_id=business.id, role=UserRole.STAFF)
    async_db.add_all([m1, m2])
    await async_db.commit()

    service = MembershipService()

    # Remove member successfully
    removed = await service.remove_member(async_db, owner, business.id, staff.id)
    assert removed.is_active is False
    assert removed.deleted_at is not None


@pytest.mark.asyncio
async def test_service_remove_member_failures(async_db):
    owner = User(clerk_id="usr_owner", email="owner@test.com")
    business = Business(business_name="Acme Corporation")

    async_db.add_all([owner, business])
    await async_db.commit()

    m1 = Membership(user_id=owner.id, business_id=business.id, role=UserRole.OWNER)
    async_db.add(m1)
    await async_db.commit()

    service = MembershipService()

    # Try to remove oneself (OWNER tries to remove OWNER - raises 400)
    with pytest.raises(HTTPException) as exc:
        await service.remove_member(async_db, owner, business.id, owner.id)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


# ==============================================================================
# 2. API Endpoints Integration Tests
# ==============================================================================
def test_api_business_context_and_members(async_db):
    client = TestClient(app)

    # Setup database records
    owner = User(
        clerk_id="usr_clerk_owner",
        email="owner@test.com",
        role=UserRole.OWNER,
        is_active=True
    )
    viewer = User(
        clerk_id="usr_clerk_viewer",
        email="viewer@test.com",
        role=UserRole.VIEWER,
        is_active=True
    )
    business = Business(business_name="Team Enterprise")

    # Run setup asynchronously
    import asyncio
    loop = asyncio.get_event_loop()

    async def db_setup():
        async_db.add_all([owner, viewer, business])
        await async_db.commit()

        m1 = Membership(user_id=owner.id, business_id=business.id, role=UserRole.OWNER)
        m2 = Membership(user_id=viewer.id, business_id=business.id, role=UserRole.VIEWER)
        async_db.add_all([m1, m2])
        await async_db.commit()
        return owner.id, viewer.id, business.id

    owner_id, viewer_id, business_id = loop.run_until_complete(db_setup())

    # Mock Dependency Overrides
    app.dependency_overrides[get_current_user] = lambda: owner
    app.dependency_overrides[get_db] = lambda: async_db

    # Mock token validation to allow middleware pass-through
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": "usr_clerk_owner"}

        # 1. Select Business Profile via POST /api/v1/businesses/select/{id}
        select_response = client.post(
            f"/api/v1/businesses/select/{business_id}",
            headers={"Authorization": "Bearer dummy"}
        )
        assert select_response.status_code == 200
        assert select_response.json()["status"] == "selected"

        # 2. Get Current Business Context via GET /api/v1/businesses/current (passing X-Business-ID)
        context_response = client.get(
            "/api/v1/businesses/current",
            headers={"Authorization": "Bearer dummy", "X-Business-ID": str(business_id)}
        )
        assert context_response.status_code == 200
        assert context_response.json()["business_name"] == "Team Enterprise"

        # 3. List Business Members via GET /api/v1/businesses/{id}/members
        members_response = client.get(
            f"/api/v1/businesses/{business_id}/members",
            headers={"Authorization": "Bearer dummy"}
        )
        assert members_response.status_code == 200
        assert len(members_response.json()) == 2

        # 4. Add new member via POST /api/v1/businesses/{id}/members (as OWNER)
        # First register target user in DB
        new_user = User(clerk_id="usr_clerk_new", email="new_member@test.com")
        async def register_new_user():
            async_db.add(new_user)
            await async_db.commit()
        loop.run_until_complete(register_new_user())

        add_payload = {
            "email": "new_member@test.com",
            "role": "staff"
        }
        add_response = client.post(
            f"/api/v1/businesses/{business_id}/members",
            json=add_payload,
            headers={"Authorization": "Bearer dummy"}
        )
        assert add_response.status_code == 201
        assert add_response.json()["role"] == "staff"

        # 5. Remove member via DELETE /api/v1/businesses/{id}/members/{user_id}
        remove_response = client.delete(
            f"/api/v1/businesses/{business_id}/members/{viewer_id}",
            headers={"Authorization": "Bearer dummy"}
        )
        assert remove_response.status_code == 200
        assert remove_response.json()["is_active"] is False
