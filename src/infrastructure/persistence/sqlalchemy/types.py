"""Custom SQLAlchemy TypeDecorators.

These live in infrastructure so the domain value objects stay pure.
Each decorator handles the round-trip:
  Python value object  ──►  DB primitive  (process_bind_param)
  DB primitive         ──►  Python value object  (process_result_value)
"""

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from src.domain.deliverable.deliverable import DeliverableStatus
from src.domain.invoice.invoice import InvoiceStatus
from src.domain.project.project import ProjectStatus
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.invoice_id import InvoiceId
from src.domain.shared.membership_id import MembershipId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserEmail, UserId, UserName


class UserIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserId(value) if value is not None else None


class UserEmailType(TypeDecorator):
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserEmail):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserEmail(value) if value is not None else None


class UserNameType(TypeDecorator):
    impl = String(100)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, UserName):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return UserName(value) if value is not None else None


class TenantIdType(TypeDecorator):
    """Maps TenantId value object ↔ String(36) UUID column."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, TenantId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return TenantId(value) if value is not None else None


class OrganizationIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, OrganizationId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return OrganizationId(value) if value is not None else None


class MembershipIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, MembershipId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return MembershipId(value) if value is not None else None


class InvitationIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, InvitationId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return InvitationId(value) if value is not None else None


class ProjectIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, ProjectId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return ProjectId(value) if value is not None else None


class DeliverableIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, DeliverableId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return DeliverableId(value) if value is not None else None


class DeliverableStatusType(TypeDecorator):
    """Maps DeliverableStatus enum ↔ String(30) column."""

    impl = String(30)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, DeliverableStatus):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return DeliverableStatus(value) if value is not None else None


class ProjectStatusType(TypeDecorator):
    """Maps ProjectStatus enum ↔ String(20) column."""

    impl = String(20)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, ProjectStatus):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return ProjectStatus(value) if value is not None else None


class RoleType(TypeDecorator):
    """Maps Role enum ↔ String column."""

    impl = String(10)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, Role):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return Role(value) if value is not None else None


class InvoiceIdType(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, InvoiceId):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return InvoiceId(value) if value is not None else None


class InvoiceStatusType(TypeDecorator):
    """Maps InvoiceStatus enum ↔ String(10) column."""

    impl = String(10)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if isinstance(value, InvoiceStatus):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        return InvoiceStatus(value) if value is not None else None
