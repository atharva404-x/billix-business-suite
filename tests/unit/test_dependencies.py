import asyncio
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.base import Base
from app.models.user import User
from app.auth.dependencies import get_current_user


@pytest.fixture
def async_db():
    # Explicitly manage a private event loop for this fixture's setup and teardown
    loop = asyncio.new_event_loop()

    # Set up async in-memory SQLite database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Materialize schemas
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    loop.run_until_complete(create_tables())

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    session = AsyncSessionLocal()

    yield session

    # Teardown the session and database resources on the same loop
    async def teardown():
        await session.close()
        await engine.dispose()

    loop.run_until_complete(teardown())
    loop.close()


@pytest.mark.asyncio
async def test_get_current_user_no_state_user_id(async_db):
    request = MagicMock()
    request.state = MagicMock()
    del request.state.user_id  # Ensure user_id is absent

    with pytest.raises(HTTPException) as exc:
        await get_current_user(request, async_db)

    assert exc.value.status_code == 401
    assert "Authentication required" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_not_found(async_db):
    request = MagicMock()
    request.state.user_id = "user_clerk_nonexistent"

    with pytest.raises(HTTPException) as exc:
        await get_current_user(request, async_db)

    assert exc.value.status_code == 401
    assert "not found or inactive" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_inactive(async_db):
    # Insert an inactive user into db
    user = User(
        clerk_id="user_clerk_inactive",
        email="inactive@example.com",
        first_name="Jane",
        last_name="Doe",
        is_active=False
    )
    async_db.add(user)
    await async_db.commit()

    request = MagicMock()
    request.state.user_id = "user_clerk_inactive"

    with pytest.raises(HTTPException) as exc:
        await get_current_user(request, async_db)

    assert exc.value.status_code == 401
    assert "not found or inactive" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_success(async_db):
    # Insert active user
    user = User(
        clerk_id="user_clerk_active",
        email="active@example.com",
        first_name="John",
        last_name="Doe",
        is_active=True
    )
    async_db.add(user)
    await async_db.commit()

    request = MagicMock()
    request.state.user_id = "user_clerk_active"

    loaded_user = await get_current_user(request, async_db)
    assert loaded_user.clerk_id == "user_clerk_active"
    assert loaded_user.email == "active@example.com"
    assert loaded_user.first_name == "John"
