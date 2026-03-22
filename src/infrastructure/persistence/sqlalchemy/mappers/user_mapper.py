"""Imperative mapping: users_table  ──►  domain User entity.

SQLAlchemy instruments the User class attributes so that:
  - Reading from DB → TypeDecorators reconstruct value objects.
  - Writing to DB   → TypeDecorators extract primitive values.

The domain User class itself has ZERO SQLAlchemy imports.

Call start_mappers() exactly once at application startup.
"""
from sqlalchemy.orm import class_mapper, registry
from sqlalchemy.orm.exc import UnmappedClassError

from src.domain.user.user import User
from src.infrastructure.persistence.sqlalchemy.tables.users_table import users_table

_mapper_registry = registry()


def start_mappers() -> None:
    """Idempotent — safe to call multiple times (e.g. in tests)."""
    try:
        class_mapper(User)
        return  # already mapped
    except UnmappedClassError:
        pass

    _mapper_registry.map_imperatively(
        User,
        users_table,
        # All columns map directly via TypeDecorators.
        # _domain_events has no column → SQLAlchemy ignores it.
    )
