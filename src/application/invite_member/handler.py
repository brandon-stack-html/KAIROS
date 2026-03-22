import structlog

from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.application.invite_member.command import InviteMemberCommand
from src.application.shared.email_sender import (
    AbstractEmailSender,
    EmailTemplate,
    build_email,
)
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.organization.invitation import Invitation
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserEmail, UserId

logger = structlog.get_logger()


class InviteMemberHandler:
    def __init__(
        self,
        uow: IOrganizationUnitOfWork,
        email_sender: AbstractEmailSender,
    ) -> None:
        self._uow = uow
        self._email_sender = email_sender

    async def handle(self, command: InviteMemberCommand) -> Invitation:
        """Returns the created Invitation."""
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(command.org_id), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(command.org_id)

            inviter_id = UserId(command.inviter_id)
            invitee_email = UserEmail(command.invitee_email)
            role = Role(command.role)

            # Validate inviter's role (raises InsufficientRoleError if not allowed)
            inviter_membership = org._get_membership(inviter_id)
            if not inviter_membership.role.can_invite():
                from src.domain.organization.errors import InsufficientRoleError

                raise InsufficientRoleError()

            invitation = Invitation.create(
                org_id=org.id.value,
                invitee_email=invitee_email,
                inviter_id=inviter_id,
                role=role,
            )

            await self._uow.invitations.save(invitation)

        # Fire-and-forget: email failure must never block the invitation.
        try:
            msg = build_email(
                EmailTemplate.INVITATION,
                {
                    "to": command.invitee_email,
                    "inviter_name": command.inviter_id,  # ID as fallback — override in your project
                    "org_name": org.name,
                    "accept_url": (
                        f"{command.frontend_url}"
                        f"/invitations/{invitation.id.value}/accept"
                    ),
                },
            )
            await self._email_sender.send(msg)
        except Exception:
            logger.warning(
                "email.invitation_failed",
                invitation_id=invitation.id.value,
                invitee=command.invitee_email,
            )

        return invitation
