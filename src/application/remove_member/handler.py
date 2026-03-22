from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.application.remove_member.command import RemoveMemberCommand
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class RemoveMemberHandler:
    def __init__(self, uow: IOrganizationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: RemoveMemberCommand) -> None:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(command.org_id), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(command.org_id)

            org.remove_member(
                remover_id=UserId(command.remover_id),
                user_id=UserId(command.user_id),
            )

            await self._uow.organizations.save(org)
