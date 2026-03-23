from src.application.get_organization.command import GetOrganizationCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.organization.organization import Organization
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId


class GetOrganizationHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetOrganizationCommand) -> Organization:
        async with self._uow:
            org_id = OrganizationId.from_str(command.org_id)
            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(org_id, tenant_id)
            if org is None:
                raise OrganizationNotFoundError(command.org_id)
            return org
