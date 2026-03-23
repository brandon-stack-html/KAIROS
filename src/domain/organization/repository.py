"""Driven ports for the Organization bounded context."""

from abc import ABC, abstractmethod

from src.domain.organization.invitation import Invitation
from src.domain.organization.organization import Organization
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserEmail, UserId


class IOrganizationRepository(ABC):
    @abstractmethod
    async def save(self, org: Organization) -> None: ...

    @abstractmethod
    async def find_by_id(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> Organization | None: ...

    @abstractmethod
    async def find_by_slug(
        self, slug: str, tenant_id: TenantId
    ) -> Organization | None: ...

    @abstractmethod
    async def find_by_user(
        self, user_id: UserId, tenant_id: TenantId
    ) -> list[Organization]: ...

    @abstractmethod
    async def exists_by_slug(self, slug: str, tenant_id: TenantId) -> bool: ...


class IInvitationRepository(ABC):
    @abstractmethod
    async def save(self, invitation: Invitation) -> None: ...

    @abstractmethod
    async def find_by_id(self, inv_id: InvitationId) -> Invitation | None: ...

    @abstractmethod
    async def find_pending_by_email(
        self, email: UserEmail, org_id: OrganizationId
    ) -> Invitation | None: ...
