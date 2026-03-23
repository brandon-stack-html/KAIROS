"""Imperative mapping: projects_table ──► Project domain class.

Call start_mappers() exactly once at application startup, AFTER
start_organization_mappers() (FK dependency on organizations).
"""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.project.project import Project
from src.infrastructure.persistence.sqlalchemy.tables.projects_table import (
    projects_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    global _mapped
    if _mapped:
        return

    try:
        class_mapper(Project)
    except UnmappedClassError:
        _mapper_registry.map_imperatively(Project, projects_table)

    _mapped = True
