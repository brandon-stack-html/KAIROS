from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class OrganizationCreated(DomainEvent):
    org_id: str
    name: str
    slug: str
    tenant_id: str
    owner_id: str


@dataclass(frozen=True, kw_only=True)
class MemberAdded(DomainEvent):
    org_id: str
    user_id: str
    role: str


@dataclass(frozen=True, kw_only=True)
class MemberRemoved(DomainEvent):
    org_id: str
    user_id: str


@dataclass(frozen=True, kw_only=True)
class MemberRoleChanged(DomainEvent):
    org_id: str
    user_id: str
    old_role: str
    new_role: str


@dataclass(frozen=True, kw_only=True)
class OrganizationDissolved(DomainEvent):
    org_id: str
    tenant_id: str


@dataclass(frozen=True, kw_only=True)
class InvitationSent(DomainEvent):
    invitation_id: str
    org_id: str
    invitee_email: str
    inviter_id: str
    role: str


@dataclass(frozen=True, kw_only=True)
class InvitationAccepted(DomainEvent):
    invitation_id: str
    org_id: str
    user_id: str
