"""Organization aggregate root.

Domain rules enforced here:
- Name: 2–100 characters (stripped).
- Slug: 2–63 lowercase alphanumeric chars or hyphens, cannot start/end with hyphen.
- create() automatically adds the owner as OWNER membership.
- add_member() requires the inviter to have OWNER or ADMIN role.
- remove_member() prevents removing the last OWNER.
- change_member_role() is restricted to OWNERs and prevents demoting the last OWNER.
- dissolve() is restricted to OWNERs.

NOT frozen — SQLAlchemy imperative mapper sets attributes on reconstruction.
"""
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.membership_id import MembershipId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId
from src.domain.organization.errors import (
    CannotRemoveLastOwnerError,
    InsufficientRoleError,
    InvalidOrgNameError,
    InvalidOrgSlugError,
    MemberAlreadyExistsError,
    MemberNotFoundError,
)
from src.domain.organization.events import (
    MemberAdded,
    MemberRemoved,
    MemberRoleChanged,
    OrganizationCreated,
    OrganizationDissolved,
)
from src.domain.organization.membership import Membership

_SLUG_RE = re.compile(r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$")


@dataclass(eq=False)
class Organization(AggregateRoot):
    """Organization aggregate root.

    Field order for @dataclass inheritance:
      id          – inherited from Entity (required)
      _domain_events – AggregateRoot (init=False)
      name / slug / tenant_id – required
      _memberships – internal collection (init=False)
      is_active / created_at – optional (have defaults)
    """

    id: OrganizationId
    name: str
    slug: str
    tenant_id: TenantId
    _memberships: list[Membership] = field(default_factory=list, init=False, repr=False)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate_name(self.name)
        self._validate_slug(self.slug)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _ensure_memberships(self) -> None:
        """Guard: SQLAlchemy bypasses __init__ — _memberships may be unset."""
        if not hasattr(self, "_memberships") or self._memberships is None:
            self._memberships = []

    def _find_membership(self, user_id: UserId) -> Membership | None:
        self._ensure_memberships()
        return next((m for m in self._memberships if m.user_id == user_id), None)

    def _get_membership(self, user_id: UserId) -> Membership:
        m = self._find_membership(user_id)
        if m is None:
            raise MemberNotFoundError(user_id.value, self.id.value)
        return m

    def _owner_count(self) -> int:
        self._ensure_memberships()
        return sum(1 for m in self._memberships if m.role is Role.OWNER)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        name: str,
        slug: str,
        owner_id: UserId,
        tenant_id: TenantId,
    ) -> "Organization":
        name = name.strip()
        slug = slug.strip().lower()
        cls._validate_name(name)
        cls._validate_slug(slug)

        org = cls(
            id=OrganizationId.generate(),
            name=name,
            slug=slug,
            tenant_id=tenant_id,
        )
        # Add owner automatically
        owner_membership = Membership(
            id=MembershipId.generate(),
            org_id=org.id,
            user_id=owner_id,
            role=Role.OWNER,
        )
        org._memberships.append(owner_membership)

        org.add_domain_event(
            OrganizationCreated(
                org_id=org.id.value,
                name=org.name,
                slug=org.slug,
                tenant_id=tenant_id.value,
                owner_id=owner_id.value,
            )
        )
        return org

    # ── Behaviour ─────────────────────────────────────────────────────────

    def add_member(
        self,
        inviter_id: UserId,
        user_id: UserId,
        role: Role,
    ) -> Membership:
        """Add a user as a member. Validates inviter's role."""
        inviter = self._get_membership(inviter_id)
        if not inviter.role.can_invite():
            raise InsufficientRoleError(
                f"Role '{inviter.role}' cannot invite members."
            )
        if self._find_membership(user_id) is not None:
            raise MemberAlreadyExistsError(user_id.value, self.id.value)

        membership = Membership(
            id=MembershipId.generate(),
            org_id=self.id,
            user_id=user_id,
            role=role,
        )
        self._ensure_memberships()
        self._memberships.append(membership)

        self.add_domain_event(
            MemberAdded(org_id=self.id.value, user_id=user_id.value, role=role.value)
        )
        return membership

    def remove_member(self, remover_id: UserId, user_id: UserId) -> None:
        """Remove a member. Cannot remove the last OWNER."""
        remover = self._get_membership(remover_id)
        if not remover.role.can_invite():
            raise InsufficientRoleError("Only OWNER or ADMIN can remove members.")

        target = self._get_membership(user_id)
        if target.role is Role.OWNER and self._owner_count() <= 1:
            raise CannotRemoveLastOwnerError()

        self._ensure_memberships()
        self._memberships = [m for m in self._memberships if m.user_id != user_id]

        self.add_domain_event(
            MemberRemoved(org_id=self.id.value, user_id=user_id.value)
        )

    def change_member_role(
        self,
        changer_id: UserId,
        user_id: UserId,
        new_role: Role,
    ) -> None:
        """Change a member's role. Only OWNERs may do this."""
        changer = self._get_membership(changer_id)
        if changer.role is not Role.OWNER:
            raise InsufficientRoleError("Only an OWNER can change member roles.")

        target = self._get_membership(user_id)
        old_role = target.role

        # Prevent demoting the last owner
        if old_role is Role.OWNER and new_role is not Role.OWNER and self._owner_count() <= 1:
            raise CannotRemoveLastOwnerError()

        target.role = new_role

        self.add_domain_event(
            MemberRoleChanged(
                org_id=self.id.value,
                user_id=user_id.value,
                old_role=old_role.value,
                new_role=new_role.value,
            )
        )

    def dissolve(self, requester_id: UserId) -> None:
        """Dissolve (soft-delete) the organization. Only OWNERs may do this."""
        requester = self._get_membership(requester_id)
        if not requester.role.can_delete_org():
            raise InsufficientRoleError("Only an OWNER can dissolve an organization.")

        self.is_active = False

        self.add_domain_event(
            OrganizationDissolved(
                org_id=self.id.value,
                tenant_id=self.tenant_id.value,
            )
        )

    @property
    def memberships(self) -> list[Membership]:
        self._ensure_memberships()
        return list(self._memberships)

    # ── Validation helpers ────────────────────────────────────────────────

    @staticmethod
    def _validate_name(name: str) -> None:
        if not (2 <= len(name) <= 100):
            raise InvalidOrgNameError(name)

    @staticmethod
    def _validate_slug(slug: str) -> None:
        if not _SLUG_RE.match(slug):
            raise InvalidOrgSlugError(slug)
