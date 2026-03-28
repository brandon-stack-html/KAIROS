"""Imperative mapping: documents_table ──► Document domain class."""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.document.document import Document
from src.infrastructure.persistence.sqlalchemy.tables.documents_table import (
    documents_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    try:
        class_mapper(Document)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Document, documents_table)

    _mapped = True
