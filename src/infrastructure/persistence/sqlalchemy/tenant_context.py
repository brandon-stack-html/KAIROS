"""Helpers for PostgreSQL Row Level Security tenant context.

set_tenant() runs `SET LOCAL app.current_tenant_id = '<uuid>'`
within the current transaction so RLS policies can filter rows.

For SQLite (used in tests) this is a no-op — tenant isolation is
enforced at the application layer (repository WHERE clauses).
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import settings


async def set_tenant(session: AsyncSession, tenant_id: str) -> None:
    """Bind tenant_id to the current DB transaction for RLS.

    No-op when DATABASE_URL points to SQLite.
    """
    if "sqlite" in settings.database_url:
        return
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": tenant_id},
    )
