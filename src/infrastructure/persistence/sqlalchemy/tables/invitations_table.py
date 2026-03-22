"""invitations table — pending invitations to join an organization."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Table

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    InvitationIdType,
    RoleType,
    UserIdType,
    UserEmailType,
)

invitations_table = Table(
    "invitations",
    metadata,
    Column("id", InvitationIdType, primary_key=True),
    Column(
        "org_id",
        String(36),           # FK — plain string, no VO needed on child entity
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("invitee_email", UserEmailType, nullable=False),
    Column(
        "inviter_id",
        UserIdType,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    ),
    Column("role", RoleType, nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("is_accepted", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # Fast lookup of pending invites for an email+org combo
    Index("ix_invitations_org_id_email", "org_id", "invitee_email"),
)
