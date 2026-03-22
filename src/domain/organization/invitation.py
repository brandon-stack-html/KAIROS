"""Invitation entity — a pending invite to join an organization.

Not an aggregate root; lifecycle is managed by the application layer
through IInvitationRepository. Domain events are collected on the
aggregate (Organization) or emitted directly by the use case handler.

NOT frozen — SQLAlchemy imperative mapper needs to set attributes.
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from src.domain.shared.entity import Entity
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.role import Role
from src.domain.organization.errors import (
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
)
from src.domain.user.user import UserId, UserEmail


_INVITATION_TTL_DAYS = 7


@dataclass(eq=False)
class Invitation(Entity[InvitationId]):
    """A pending invitation for a user to join an organization."""

    id: InvitationId
    org_id: str
    invitee_email: UserEmail
    inviter_id: UserId
    role: Role
    expires_at: datetime
    is_accepted: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        org_id: str,
        invitee_email: UserEmail,
        inviter_id: UserId,
        role: Role,
    ) -> "Invitation":
        now = datetime.now(UTC)
        return cls(
            id=InvitationId.generate(),
            org_id=org_id,
            invitee_email=invitee_email,
            inviter_id=inviter_id,
            role=role,
            expires_at=now + timedelta(days=_INVITATION_TTL_DAYS),
            created_at=now,
        )

    # ── Behaviour ─────────────────────────────────────────────────────────

    def is_expired(self) -> bool:
        now = datetime.now(UTC)
        expires = self.expires_at
        # SQLite strips timezone — normalise to UTC before comparison
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return now > expires

    def accept(self) -> None:
        """Mark as accepted; caller must add member to the organization."""
        if self.is_expired():
            raise InvitationExpiredError()
        if self.is_accepted:
            raise InvitationAlreadyAcceptedError()
        self.is_accepted = True
