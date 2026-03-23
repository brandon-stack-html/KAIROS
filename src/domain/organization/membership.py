"""Membership entity — represents a user's participation in an organization.

Not an aggregate root; lifecycle is managed by Organization.
NOT frozen — SQLAlchemy imperative mapper sets attributes on reconstruction.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.shared.entity import Entity
from src.domain.shared.membership_id import MembershipId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.user.user import UserId


@dataclass(eq=False)
class Membership(Entity[MembershipId]):
    """A user's membership in an organization with a specific role.

    org_id is OrganizationId (not str) because SQLAlchemy's imperative mapper
    uses OrganizationIdType for the org_id column, which sets this attribute to
    an OrganizationId VO on DB reconstruction. Using the VO type here keeps
    the type consistent at runtime.
    """

    id: MembershipId
    org_id: OrganizationId
    user_id: UserId
    role: Role
    joined_at: datetime = field(default_factory=lambda: datetime.now(UTC))
