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
from app.schemas.business import BusinessCreate, BusinessUpdate
from app.services.business import BusinessService
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
# 1. BusinessService Direct Methods Unit Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_service_create_business_success(async_db):
    user = User(clerk_id="usr_clerk_1", email="one@example.com")
    async_db.add(user)
    await async_db.commit()

    service = BusinessService()
    business_create = BusinessCreate(
        business_name="Test Enterprise",
        gstin="27AADCA1234F1Z5",
        pan="AADCA1234F",
        email="info@test.com"
    )

    business = await service.create_business(async_db, user, business_create)
    assert business.business_name == "Test Enterprise"
    assert business.gstin == "27AADCA1234F1Z5"

    # Verify that creator OWNER membership was automatically configured
    from sqlalchemy.orm import selectinload
    query = select(User).where(User.id == user.id).options(
        selectinload(User.memberships).selectinload(Membership.business)
    )
    res = await async_db.execute(query)
    loaded_user = res.scalar_one()

    assert len(loaded_user.memberships) == 1
    assert loaded_user.memberships[0].role == UserRole.OWNER
    assert loaded_user.memberships[0].business_id == business.id


@pytest.mark.asyncio
async def test_service_create_business_duplicate_gstin(async_db):
    user = User(clerk_id="usr_clerk_1", email="one@example.com")
    existing_biz = Business(business_name="Existing Enterprise", gstin="27AADCA1234F1Z5")
    async_db.add_all([user, existing_biz])
    await async_db.commit()

    service = BusinessService()
    business_create = BusinessCreate(
        business_name="Test Enterprise New",
        gstin="27AADCA1234F1Z5"  # Pre-existing GSTIN
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_business(async_db, user, business_create)

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc.value.detail


@pytest.mark.asyncio
async def test_service_get_business_authorization(async_db):
    user = User(clerk_id="usr_clerk_1", email="one@example.com")
    other_user = User(clerk_id="usr_clerk_2", email="two@example.com")
    business = Business(business_name="Secret Enterprise")

    async_db.add_all([user, other_user, business])
    await async_db.commit()

    # User is OWNER
    membership = Membership(user_id=user.id, business_id=business.id, role=UserRole.OWNER)
    async_db.add(membership)
    await async_db.commit()

    service = BusinessService()

    # 1. OWNER retrieves details successfully
    loaded_biz = await service.get_business_by_id(async_db, user, business.id)
    assert loaded_biz.business_name == "Secret Enterprise"

    # 2. Other user tries to retrieve details (should raise 403)
    with pytest.raises(HTTPException) as exc:
        await service.get_business_by_id(async_db, other_user, business.id)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_service_update_and_deactivate_checks(async_db):
    user = User(clerk_id="usr_clerk_owner", email="owner@example.com")
    staff = User(clerk_id="usr_clerk_staff", email="staff@example.com")
    business = Business(business_name="Alice Corp", gstin="27AADCA1234F1Z5")

    async_db.add_all([user, staff, business])
    await async_db.commit()

    # OWNER and STAFF memberships
    m1 = Membership(user_id=user.id, business_id=business.id, role=UserRole.OWNER)
    m2 = Membership(user_id=staff.id, business_id=business.id, role=UserRole.STAFF)
    async_db.add_all([m1, m2])
    await async_db.commit()

    service = BusinessService()

    # 1. Staff tries to update business (raises 403)
    with pytest.raises(HTTPException) as exc:
        await service.update_business(async_db, staff, business.id, BusinessUpdate(business_name="Staff Hack"))
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    # 2. Owner updates business successfully
    updated = await service.update_business(async_db, user, business.id, BusinessUpdate(business_name="Alice Big Corp"))
    assert updated.business_name == "Alice Big Corp"

    # 3. Staff deactivates business (raises 403)
    with pytest.raises(HTTPException) as exc:
        await service.deactivate_business(async_db, staff, business.id)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN

    # 4. Owner deactivates business successfully
    deactivated = await service.deactivate_business(async_db, user, business.id)
    assert deactivated.is_active is False
    assert deactivated.deleted_at is not None


# ==============================================================================
# 2. REST API Endpoints Integration Tests
# ==============================================================================
def test_api_endpoints_workflow(async_db):
    client = TestClient(app)

    # Mock user and database session dependencies
    mock_user = User(
        clerk_id="usr_clerk_endpoint",
        email="api@example.com",
        role=UserRole.MANAGER,
        is_active=True
    )
    mock_user.id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: async_db

    # Patch AuthMiddleware token verification to let it pass
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": "usr_clerk_endpoint"}

        # 1. Create Business Profile via POST /api/v1/businesses
        payload = {
            "business_name": "API Enterprise Pvt Ltd",
            "legal_name": "API Enterprise",
            "gstin": "27AADCA1234F1Z5",
            "email": "contact@api.com",
            "country": "India"
        }

        response = client.post("/api/v1/businesses/", json=payload, headers={"Authorization": "Bearer dummy_token"})
        assert response.status_code == 201

        biz_data = response.json()
        assert biz_data["business_name"] == "API Enterprise Pvt Ltd"
        biz_id = biz_data["id"]

        # 2. List Business Profiles via GET /api/v1/businesses
        list_response = client.get("/api/v1/businesses/", headers={"Authorization": "Bearer dummy_token"})
        assert list_response.status_code == 200

        list_data = list_response.json()
        assert len(list_data) == 1
        assert list_data[0]["id"] == biz_id

        # 3. Retrieve specific details via GET /api/v1/businesses/{id}
        get_response = client.get(f"/api/v1/businesses/{biz_id}", headers={"Authorization": "Bearer dummy_token"})
        assert get_response.status_code == 200
        assert get_response.json()["business_name"] == "API Enterprise Pvt Ltd"

        # 4. Update Business via PATCH /api/v1/businesses/{id}
        patch_payload = {"business_name": "API Enterprise Updated"}
        patch_response = client.patch(f"/api/v1/businesses/{biz_id}", json=patch_payload, headers={"Authorization": "Bearer dummy_token"})
        assert patch_response.status_code == 200
        assert patch_response.json()["business_name"] == "API Enterprise Updated"

        # 5. Deactivate Business via DELETE /api/v1/businesses/{id}
        delete_response = client.delete(f"/api/v1/businesses/{biz_id}", headers={"Authorization": "Bearer dummy_token"})
        assert delete_response.status_code == 200
        assert delete_response.json()["is_active"] is False
