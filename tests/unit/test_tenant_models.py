import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.models.base import Base
from app.models.user import User
from app.models.business import Business
from app.models.membership import Membership
from app.models.roles import UserRole


@pytest_asyncio.fixture
async def async_db():
    # Set up async in-memory SQLite database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Materialize schemas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_business_creation_and_defaults(async_db):
    business = Business(
        business_name="Acme Corporation",
        legal_name="Acme Corp Private Limited",
        gstin="27AADCA1234F1Z5",
        pan="AADCA1234F"
    )
    async_db.add(business)
    await async_db.commit()

    # Load and verify fields and defaults
    result = await async_db.execute(select(Business).where(Business.business_name == "Acme Corporation"))
    loaded_business = result.scalar_one()

    assert loaded_business.id is not None
    assert loaded_business.legal_name == "Acme Corp Private Limited"
    assert loaded_business.gstin == "27AADCA1234F1Z5"
    assert loaded_business.pan == "AADCA1234F"
    assert loaded_business.country == "India"
    assert loaded_business.currency == "INR"
    assert loaded_business.timezone == "Asia/Kolkata"
    assert loaded_business.invoice_start_number == 1
    assert loaded_business.is_active is True


@pytest.mark.asyncio
async def test_user_business_membership_relationship(async_db):
    # Create User
    user = User(
        clerk_id="user_clerk_owner",
        email="owner@example.com",
        first_name="Alice",
        role=UserRole.OWNER
    )
    # Create Business
    business = Business(business_name="Alice Enterprise")

    async_db.add_all([user, business])
    await async_db.commit()

    # Create Membership
    membership = Membership(
        user_id=user.id,
        business_id=business.id,
        role=UserRole.OWNER
    )
    async_db.add(membership)
    await async_db.commit()

    # Query user to verify memberships relation with selectinload to prevent lazy-load errors
    from sqlalchemy.orm import selectinload
    query = select(User).where(User.clerk_id == "user_clerk_owner").options(
        selectinload(User.memberships).selectinload(Membership.business)
    )
    result = await async_db.execute(query)
    loaded_user = result.scalar_one()

    assert len(loaded_user.memberships) == 1
    assert loaded_user.memberships[0].role == UserRole.OWNER
    assert loaded_user.memberships[0].business.business_name == "Alice Enterprise"


@pytest.mark.asyncio
async def test_cascade_delete_user(async_db):
    user = User(clerk_id="user_test_delete", email="test@example.com")
    business = Business(business_name="Test Business")
    async_db.add_all([user, business])
    await async_db.commit()

    membership = Membership(user_id=user.id, business_id=business.id, role=UserRole.STAFF)
    async_db.add(membership)
    await async_db.commit()

    # Verify membership exists
    result = await async_db.execute(select(Membership).where(Membership.id == membership.id))
    assert result.scalar_one_or_none() is not None

    # Delete User
    await async_db.delete(user)
    await async_db.commit()

    # Verify membership is deleted (cascade delete on user)
    result = await async_db.execute(select(Membership).where(Membership.id == membership.id))
    assert result.scalar_one_or_none() is None

    # Verify business is NOT deleted
    result = await async_db.execute(select(Business).where(Business.id == business.id))
    assert result.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_cascade_delete_business(async_db):
    user = User(clerk_id="user_test_delete_biz", email="test2@example.com")
    business = Business(business_name="Test Business 2")
    async_db.add_all([user, business])
    await async_db.commit()

    membership = Membership(user_id=user.id, business_id=business.id, role=UserRole.ADMIN)
    async_db.add(membership)
    await async_db.commit()

    # Delete Business
    await async_db.delete(business)
    await async_db.commit()

    # Verify membership is deleted (cascade delete on business)
    result = await async_db.execute(select(Membership).where(Membership.id == membership.id))
    assert result.scalar_one_or_none() is None

    # Verify user is NOT deleted
    result = await async_db.execute(select(User).where(User.id == user.id))
    assert result.scalar_one_or_none() is not None
