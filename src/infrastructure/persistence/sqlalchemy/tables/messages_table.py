"""messages table — pure SQLAlchemy Table definition."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, Text

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    ConversationIdType,
    MessageIdType,
    UserIdType,
)

messages_table = Table(
    "messages",
    metadata,
    Column("id", MessageIdType, primary_key=True),
    Column(
        "conversation_id",
        ConversationIdType,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("sender_id", UserIdType, nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Index("ix_messages_conversation_created", "conversation_id", "created_at"),
)
