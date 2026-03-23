from src.application.get_tenant_by_slug.command import GetTenantBySlugCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.tenant.errors import TenantNotFoundError
from src.domain.tenant.tenant import Tenant


class GetTenantBySlugHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetTenantBySlugCommand) -> Tenant:
        async with self._uow:
            tenant = await self._uow.tenants.find_by_slug(command.slug)
            if tenant is None:
                raise TenantNotFoundError(command.slug)
            return tenant
