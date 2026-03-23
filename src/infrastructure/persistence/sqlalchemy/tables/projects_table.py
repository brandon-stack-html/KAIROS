"""projects table — pure SQLAlchemy Table definition (imperative mapping)."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table, Text

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    OrganizationIdType,
    ProjectIdType,
    ProjectStatusType,
    TenantIdType,
)

projects_table = Table(
    "projects",
    metadata,
    Column("id", ProjectIdType, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("description", Text, nullable=False, default=""),
    Column(
        "org_id",
        OrganizationIdType,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "tenant_id",
        TenantIdType,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("status", ProjectStatusType, nullable=False, default="ACTIVE"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_projects_tenant_id_org_id", "tenant_id", "org_id"),
)
