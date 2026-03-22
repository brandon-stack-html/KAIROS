from src.application.accept_invitation.command import AcceptInvitationCommand
from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.organization.organization import Organization
from src.domain.shared.errors import EntityNotFoundError
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class AcceptInvitationHandler:
    def __init__(self, uow: IOrganizationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: AcceptInvitationCommand) -> Organization:
        """Accepts the invitation, adds user to org. Returns the updated Organization."""
        async with self._uow:
            invitation = await self._uow.invitations.find_by_id(
                InvitationId.from_str(command.invitation_id)
            )
            if invitation is None:
                raise EntityNotFoundError(
                    f"Invitation '{command.invitation_id}' not found."
                )

            # Validate + mark accepted (raises InvitationExpiredError / InvitationAlreadyAcceptedError)
            invitation.accept()

            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(invitation.org_id), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(invitation.org_id)

            user_id = UserId(command.user_id)
            org.add_member(
                inviter_id=invitation.inviter_id,
                user_id=user_id,
                role=invitation.role,
            )

            await self._uow.invitations.save(invitation)
            await self._uow.organizations.save(org)

        return org
