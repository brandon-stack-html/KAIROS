"""Generic async SQLAlchemy repository.

Provides base CRUD + paginated listing for any domain entity.
Domain layer has zero knowledge of this class — it only knows
the abstract repository interface (port) defined in domain/.
"""
from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.shared.entity import Entity

TEntity = TypeVar("TEntity", bound=Entity)


@dataclass
class Page(Generic[TEntity]):
    items: list[TEntity]
    total: int
    page: int
    page_size: int

    @property
    def pages(self) -> int:
        if self.page_size == 0:
            return 0
        return -(-self.total // self.page_size)  # ceil division


class SqlAlchemyRepository(Generic[TEntity]):
    """Generic repository — subclass and set `_entity_class`.

    Example::

        class SqlAlchemyUserRepository(
            SqlAlchemyRepository[User], IUserRepository
        ):
            _entity_class = User
            ...  # add domain-specific query methods here
    """

    _entity_class: type[TEntity]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Basic CRUD ────────────────────────────────────────────────────────

    async def add(self, entity: TEntity) -> None:
        """Persist a new entity (or merge if already tracked)."""
        self._session.add(entity)

    async def get_by_id(self, entity_id: object) -> TEntity | None:
        """Return entity by primary key, or None if not found."""
        result = await self._session.execute(
            select(self._entity_class).where(
                self._entity_class.id == entity_id  # type: ignore[attr-defined]
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, entity: TEntity) -> None:
        """Mark entity for deletion (flushed on UoW commit)."""
        await self._session.delete(entity)

    # ── Pagination ────────────────────────────────────────────────────────

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> Page[TEntity]:
        """Return a page of entities with total count metadata.

        Args:
            page: 1-based page number.
            page_size: Number of items per page (max enforced by caller).
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        offset = (page - 1) * page_size

        count_result = await self._session.execute(
            select(func.count()).select_from(self._entity_class)
        )
        total: int = count_result.scalar_one()

        items_result = await self._session.execute(
            select(self._entity_class).offset(offset).limit(page_size)
        )
        items = list(items_result.scalars().all())

        return Page(items=items, total=total, page=page, page_size=page_size)
