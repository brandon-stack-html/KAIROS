"""Imperative SQLAlchemy mapper for RefreshToken."""
from sqlalchemy.orm import registry

from src.domain.shared.refresh_token import RefreshToken
from src.infrastructure.persistence.sqlalchemy.tables.refresh_tokens_table import (
    refresh_tokens_table,
)

_mapper_registry = registry()
_mapped = False


def start_mappers() -> None:
    global _mapped
    if _mapped:
        return
    _mapper_registry.map_imperatively(RefreshToken, refresh_tokens_table)
    _mapped = True
