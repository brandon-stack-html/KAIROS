"""Imperative mapping: deliverables_table ──► Deliverable domain class.

Call start_mappers() exactly once at application startup, AFTER
start_project_mappers() (FK dependency on projects).
"""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.deliverable.deliverable import Deliverable
from src.infrastructure.persistence.sqlalchemy.tables.deliverables_table import (
    deliverables_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    try:
        class_mapper(Deliverable)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Deliverable, deliverables_table)

    _mapped = True
