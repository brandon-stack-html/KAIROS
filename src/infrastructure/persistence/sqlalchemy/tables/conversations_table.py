"""conversations table — pure SQLAlchemy Table definition."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    ConversationIdType,
    ConversationTypeType,
    OrganizationIdType,
    ProjectIdType,
)

conversations_table = Table(
    "conversations",
    metadata,
    Column("id", ConversationIdType, primary_key=True),
    Column(
        "org_id",
        OrganizationIdType,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("type", ConversationTypeType, nullable=False),
    Column(
        "project_id",
        ProjectIdType,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    ),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_conversations_org_id_type", "org_id", "type"),
)
