"""SqlAlchemyOrganizationRepository — tenant-scoped organization queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.organization.organization import Organization
from src.domain.organization.repository import IOrganizationRepository
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId
from src.infrastructure.persistence.sqlalchemy.tables.memberships_table import (
    memberships_table,
)
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyOrganizationRepository(
    SqlAlchemyRepository[Organization], IOrganizationRepository
):
    _entity_class = Organization

    def __init__(self, session: AsyncSession, tenant_id: str | None = None) -> None:
        super().__init__(session)
        self._tenant_id = tenant_id

    def _tenant_filter(self, stmt):
        if self._tenant_id is not None:
            stmt = stmt.where(Organization.tenant_id == self._tenant_id)  # type: ignore[attr-defined]
        return stmt

    async def save(self, org: Organization) -> None:
        """Upsert the aggregate and its membership collection."""
        await self._session.merge(org)

    async def find_by_id(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.id == org_id)  # type: ignore[attr-defined]
            .where(Organization.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_slug(self, slug: str, tenant_id: TenantId) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.slug == slug)  # type: ignore[attr-defined]
            .where(Organization.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user(
        self, user_id: UserId, tenant_id: TenantId
    ) -> list[Organization]:
        """Return all active organizations the user belongs to within the tenant."""
        stmt = (
            select(Organization)
            .join(
                memberships_table,
                Organization.id == memberships_table.c.org_id,  # type: ignore[attr-defined]
            )
            .where(memberships_table.c.user_id == user_id)
            .where(Organization.tenant_id == tenant_id)  # type: ignore[attr-defined]
            .where(Organization.is_active.is_(True))  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())

    async def exists_by_slug(self, slug: str, tenant_id: TenantId) -> bool:
        stmt = (
            select(Organization.id)  # type: ignore[attr-defined]
            .where(Organization.slug == slug)  # type: ignore[attr-defined]
            .where(Organization.tenant_id == tenant_id)  # type: ignore[attr-defined]
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.first() is not None
