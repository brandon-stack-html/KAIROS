"""Imperative mapping: invitations_table ──► domain Invitation entity."""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.organization.invitation import Invitation
from src.infrastructure.persistence.sqlalchemy.tables.invitations_table import (
    invitations_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return
    try:
        class_mapper(Invitation)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Invitation, invitations_table)
    _mapped = True
