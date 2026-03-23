"""tenants table — pure SQLAlchemy Table definition (imperative mapping)."""

from sqlalchemy import Boolean, Column, DateTime, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import TenantIdType

tenants_table = Table(
    "tenants",
    metadata,
    Column("id", TenantIdType, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("slug", String(63), unique=True, nullable=False, index=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
