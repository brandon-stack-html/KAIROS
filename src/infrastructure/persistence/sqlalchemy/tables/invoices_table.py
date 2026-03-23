"""invoices table — pure SQLAlchemy Table definition (imperative mapping)."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Numeric, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    InvoiceIdType,
    InvoiceStatusType,
    OrganizationIdType,
    TenantIdType,
)

invoices_table = Table(
    "invoices",
    metadata,
    Column("id", InvoiceIdType, primary_key=True),
    Column("title", String(100), nullable=False),
    Column("amount", Numeric(12, 2), nullable=False),
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
    Column("status", InvoiceStatusType, nullable=False, default="DRAFT"),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("paid_at", DateTime(timezone=True), nullable=True),
    Index("ix_invoices_tenant_id_org_id", "tenant_id", "org_id"),
)
