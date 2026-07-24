import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.base import Base
from app.main import app
from app.core.database import get_db, get_db_session

@pytest_asyncio.fixture
async def db_session():
    # Set up async in-memory SQLite database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Materialize schemas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()

@pytest.fixture(autouse=True)
def override_db(db_session):
    async def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_db_session] = _get_test_db
    yield
    app.dependency_overrides.clear()
