"""Imperative mapping: tenants_table ──► domain Tenant entity."""

from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tables.tenants_table import tenants_table

_mapper_registry = registry()


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    try:
        class_mapper(Tenant)
        return  # already mapped
    except UnmappedClassError:
        pass

    _mapper_registry.map_imperatively(Tenant, tenants_table)
