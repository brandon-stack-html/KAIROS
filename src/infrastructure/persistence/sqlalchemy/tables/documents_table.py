"""documents table — pure SQLAlchemy Table definition."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    DocumentIdType,
    OrganizationIdType,
    ProjectIdType,
    UserIdType,
)

documents_table = Table(
    "documents",
    metadata,
    Column("id", DocumentIdType, primary_key=True),
    Column(
        "org_id",
        OrganizationIdType,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "project_id",
        ProjectIdType,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    ),
    Column("uploaded_by", UserIdType, nullable=False),
    Column("filename", String(255), nullable=False),
    Column("file_type", String(100), nullable=False),
    Column("file_size_bytes", Integer, nullable=False),
    Column("storage_path", String(500), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
