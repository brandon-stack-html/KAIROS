"""Imperative mapping: messages_table ──► Message domain class."""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.message.message import Message
from src.infrastructure.persistence.sqlalchemy.tables.messages_table import (
    messages_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    try:
        class_mapper(Message)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Message, messages_table)

    _mapped = True
