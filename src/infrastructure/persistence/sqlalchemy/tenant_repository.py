from sqlalchemy import select

from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.repository import ITenantRepository
from src.domain.tenant.tenant import Tenant
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyTenantRepository(SqlAlchemyRepository[Tenant], ITenantRepository):
    _entity_class = Tenant

    async def save(self, tenant: Tenant) -> None:
        await self.add(tenant)

    async def find_by_id(self, tenant_id: TenantId) -> Tenant | None:
        return await self.get_by_id(tenant_id)

    async def find_by_slug(self, slug: str) -> Tenant | None:
        result = await self._session.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        return result.scalar_one_or_none()

    async def exists_by_slug(self, slug: str) -> bool:
        result = await self._session.execute(
            select(Tenant.id).where(Tenant.slug == slug).limit(1)
        )
        return result.first() is not None
