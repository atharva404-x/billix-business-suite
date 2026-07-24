import logging
from typing import AsyncGenerator
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

logger = logging.getLogger("app.core.database")

def _clean_db_url(db_url: str) -> str:
    """Remove sslmode query parameter if using asyncpg, since it's not supported directly by asyncpg."""
    if db_url.startswith("postgresql+asyncpg://"):
        parts = urlsplit(db_url)
        if parts.query:
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            if "sslmode" in query:
                query.pop("sslmode")
            new_query = urlencode(query)
            db_url = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
    return db_url

db_url = _clean_db_url(settings.DATABASE_URL)

# Create async database engine with pool optimization
connect_args = {}
engine_kwargs = {"echo": False}

if db_url.startswith("sqlite"):
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
    db_url,
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
