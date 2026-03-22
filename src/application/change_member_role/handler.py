from src.application.change_member_role.command import ChangeMemberRoleCommand
from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.organization.organization import Organization
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class ChangeMemberRoleHandler:
    def __init__(self, uow: IOrganizationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ChangeMemberRoleCommand) -> Organization:
        """Returns the updated Organization so caller can read the new role."""
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(command.org_id), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(command.org_id)

            org.change_member_role(
                changer_id=UserId(command.changer_id),
                user_id=UserId(command.user_id),
                new_role=Role(command.new_role),
            )

            await self._uow.organizations.save(org)

        return org
