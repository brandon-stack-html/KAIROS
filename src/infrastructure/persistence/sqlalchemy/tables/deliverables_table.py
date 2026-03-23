"""deliverables table — pure SQLAlchemy Table definition (imperative mapping)."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    DeliverableIdType,
    DeliverableStatusType,
    ProjectIdType,
    TenantIdType,
)

deliverables_table = Table(
    "deliverables",
    metadata,
    Column("id", DeliverableIdType, primary_key=True),
    Column("title", String(100), nullable=False),
    Column("url_link", String(2048), nullable=False),
    Column(
        "project_id",
        ProjectIdType,
        ForeignKey("projects.id", ondelete="CASCADE"),
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
    Column("status", DeliverableStatusType, nullable=False, default="PENDING"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Index("ix_deliverables_tenant_id_project_id", "tenant_id", "project_id"),
)
