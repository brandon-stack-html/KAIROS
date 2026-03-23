"""SqlAlchemyDeliverableRepository — tenant-scoped deliverable queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.deliverable.deliverable import Deliverable
from src.domain.deliverable.repository import IDeliverableRepository
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyDeliverableRepository(
    SqlAlchemyRepository[Deliverable], IDeliverableRepository
):
    _entity_class = Deliverable

    def __init__(self, session: AsyncSession, tenant_id: str | None = None) -> None:
        super().__init__(session)
        self._tenant_id = tenant_id

    async def save(self, deliverable: Deliverable) -> None:
        """Upsert the deliverable aggregate."""
        await self._session.merge(deliverable)

    async def find_by_id(
        self, deliverable_id: DeliverableId, tenant_id: TenantId
    ) -> Deliverable | None:
        stmt = (
            select(Deliverable)
            .where(Deliverable.id == deliverable_id)  # type: ignore[attr-defined]
            .where(Deliverable.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_project(
        self, project_id: ProjectId, tenant_id: TenantId
    ) -> list[Deliverable]:
        stmt = (
            select(Deliverable)
            .where(Deliverable.project_id == project_id)  # type: ignore[attr-defined]
            .where(Deliverable.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
