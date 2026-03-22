from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.application.list_organizations.command import ListOrganizationsCommand
from src.domain.organization.organization import Organization
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class ListOrganizationsHandler:
    def __init__(self, uow: IOrganizationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListOrganizationsCommand) -> list[Organization]:
        async with self._uow:
            orgs = await self._uow.organizations.find_by_user(
                UserId(command.user_id),
                TenantId.from_str(command.tenant_id),
            )
        return orgs
