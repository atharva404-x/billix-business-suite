from logging.config import fileConfig
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import engine_from_config, pool, Table, Column, String, inspect, MetaData
import sqlalchemy as sa

from alembic import context
from alembic.ddl.impl import DefaultImpl
from app.core.config import settings
from app.models.base import Base

# Customize version table column size to accommodate descriptive/long revision IDs
def custom_version_table_impl(
    self,
    *,
    version_table: str,
    version_table_schema=None,
    version_table_pk: bool = True,
    **kw
) -> Table:
    return Table(
        version_table,
        MetaData(),
        Column("version_num", String(255), primary_key=version_table_pk),
        schema=version_table_schema,
    )

DefaultImpl.version_table_impl = custom_version_table_impl
from app.models.user import User  # noqa: F401
from app.models.business import BusinessProfile, BusinessMember  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
from app.models.unit import Unit  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.inventory import InventoryTransaction  # noqa: F401
from app.models.invoice import Invoice, InvoiceItem  # noqa: F401
from app.models.settings import BusinessSettings, BusinessPreferences  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


def _sync_migration_url(db_url: str) -> str:
    """Convert async SQLAlchemy URLs to a sync URL suitable for Alembic."""
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

    # Convert async SQLite driver to synchronous — aiosqlite cannot run in the
    # synchronous migration context and raises MissingGreenlet otherwise.
    if db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite://", 1)

    parts = urlsplit(db_url)
    if parts.scheme.startswith("postgresql") and parts.query:
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if "ssl" in query and "sslmode" not in query:
            query["sslmode"] = query.pop("ssl")
        new_query = urlencode(query)
        db_url = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

    return db_url


config.set_main_option("sqlalchemy.url", _sync_migration_url(settings.DATABASE_URL))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Check if the alembic version table exists, and if so, alter the column type in PostgreSQL
        version_table_name = config.get_main_option("version_table", "alembic_version")
        if not version_table_name:
            version_table_name = "alembic_version"

        inspector = inspect(connection)
        tables = inspector.get_table_names()

        if version_table_name in tables:
            if connection.dialect.name == "postgresql":
                # Execute the ALTER statement to increase version_num VARCHAR size to 255
                alter_stmt = sa.text(f"ALTER TABLE {version_table_name} ALTER COLUMN version_num TYPE VARCHAR(255)")
                connection.execute(alter_stmt)

        # Commit any implicitly started transactions to ensure changes are persisted
        # and the connection transaction state is clean before Alembic configure.
        if connection.in_transaction():
            connection.commit()

        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
