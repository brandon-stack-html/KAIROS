"""memberships table — user membership in an organization."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, Table, UniqueConstraint

from src.infrastructure.persistence.sqlalchemy.database import metadata
from src.infrastructure.persistence.sqlalchemy.types import (
    MembershipIdType,
    OrganizationIdType,
    RoleType,
    UserIdType,
)

memberships_table = Table(
    "memberships",
    metadata,
    Column("id", MembershipIdType, primary_key=True),
    Column(
        "org_id",
        OrganizationIdType,  # TypeDecorator handles VO↔str; SA cascade sets this from org.id
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "user_id",
        UserIdType,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("role", RoleType, nullable=False),
    Column("joined_at", DateTime(timezone=True), nullable=False),
    # A user can only have one membership per organization
    UniqueConstraint("org_id", "user_id", name="uq_memberships_org_user"),
    Index("ix_memberships_org_id_user_id", "org_id", "user_id"),
)
