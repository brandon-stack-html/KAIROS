from src.application.create_tenant.command import CreateTenantCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.tenant.errors import SlugAlreadyTakenError
from src.domain.tenant.tenant import Tenant


class CreateTenantHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateTenantCommand) -> Tenant:
        async with self._uow:
            if await self._uow.tenants.exists_by_slug(command.slug):
                raise SlugAlreadyTakenError(command.slug)
            tenant = Tenant.provision(name=command.name, slug=command.slug)
            await self._uow.tenants.save(tenant)
            return tenant
