"""organizations table — pure SQLAlchemy Table definition (imperative mapping)."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import OrganizationIdType, TenantIdType

organizations_table = Table(
    "organizations",
    metadata,
    Column("id", OrganizationIdType, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("slug", String(63), nullable=False),
    Column(
        "tenant_id",
        TenantIdType,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # Slug must be unique within a tenant
    Index("ix_organizations_tenant_id_slug", "tenant_id", "slug", unique=True),
)
