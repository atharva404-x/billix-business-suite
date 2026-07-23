import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

logger = logging.getLogger("app.core.database")

# Create async database engine with pool optimization
connect_args = {}
engine_kwargs = {"echo": False}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Neon PostgreSQL and cloud database SSL connection support for asyncpg
    if "sslmode=require" in settings.DATABASE_URL or "neon.tech" in settings.DATABASE_URL:
        connect_args["ssl"] = "require"

    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    })

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for obtaining an asynchronous database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session exception, rolling back: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Backwards-compatible dependency name used by the API routers.  A request owns
# one session and one transaction; repositories deliberately never commit.
get_db_session = get_db
