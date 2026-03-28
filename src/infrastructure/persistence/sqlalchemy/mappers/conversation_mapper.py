"""Imperative mapping: conversations_table ──► Conversation domain class."""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.conversation.conversation import Conversation
from src.infrastructure.persistence.sqlalchemy.tables.conversations_table import (
    conversations_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    try:
        class_mapper(Conversation)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Conversation, conversations_table)

    _mapped = True
