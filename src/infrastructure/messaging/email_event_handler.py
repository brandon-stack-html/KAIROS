"""EmailEventHandler — reacts to domain events by sending emails.

Pattern: domain event → event handler → email adapter.
Use cases that need event-driven emails:
  - InvitationSent → INVITATION email

This handler is wired to the event publisher in the composition root.
The use case publishes the event; this handler sends the email.
The use case itself remains unaware of email infrastructure.
"""
import structlog

from src.application.shared.email_sender import (
    AbstractEmailSender,
    EmailTemplate,
    build_email,
)
from src.domain.organization.events import InvitationSent

logger = structlog.get_logger()


class EmailEventHandler:
    def __init__(
        self,
        email_sender: AbstractEmailSender,
        frontend_url: str = "http://localhost:3000",
    ) -> None:
        self._email_sender = email_sender
        self._frontend_url = frontend_url

    async def handle_invitation_sent(self, event: InvitationSent) -> None:
        """Send an invitation email when InvitationSent domain event is published."""
        try:
            msg = build_email(
                EmailTemplate.INVITATION,
                {
                    "to": event.invitee_email,
                    "inviter_name": event.inviter_id,
                    "org_name": event.org_id,  # org name not in event — override as needed
                    "accept_url": (
                        f"{self._frontend_url}"
                        f"/invitations/{event.invitation_id}/accept"
                    ),
                },
            )
            await self._email_sender.send(msg)
        except Exception:
            logger.warning(
                "email.invitation_event_failed",
                invitation_id=event.invitation_id,
                invitee=event.invitee_email,
            )
