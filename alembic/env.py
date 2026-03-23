"""Alembic env.py — configured for async SQLAlchemy + Imperative Mapping.

Key points:
- target_metadata comes from the shared MetaData object in database.py
- All Table modules MUST be imported before target_metadata is assigned
  so that autogenerate can detect schema changes
- Online migrations run via run_sync() since the engine is async
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── 2. Import ALL table modules explicitly so autogenerate sees them ──
# Add one import per aggregate as you create new tables.
import src.infrastructure.persistence.sqlalchemy.tables.refresh_tokens_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.tenants_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.users_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.organizations_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.memberships_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.invitations_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.projects_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.deliverables_table  # noqa: F401
import src.infrastructure.persistence.sqlalchemy.tables.invoices_table  # noqa: F401
from alembic import context

# ── 1. Import shared metadata ─────────────────────────────────────────
from src.infrastructure.persistence.sqlalchemy.database import metadata

# ── 3. Assign target metadata ─────────────────────────────────────────
target_metadata = metadata

# ── Alembic Config ────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL script)."""
    from src.infrastructure.config.settings import settings

    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations via run_sync."""
    from src.infrastructure.config.settings import settings

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
