"""Driven ports for the Project bounded context."""

from abc import ABC, abstractmethod

from src.domain.project.project import Project
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class IProjectRepository(ABC):
    @abstractmethod
    async def save(self, project: Project) -> None: ...

    @abstractmethod
    async def find_by_id(
        self, project_id: ProjectId, tenant_id: TenantId
    ) -> Project | None: ...

    @abstractmethod
    async def find_by_org(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> list[Project]: ...

    @abstractmethod
    async def find_by_user_orgs(
        self, user_id: UserId, tenant_id: TenantId
    ) -> list[Project]: ...
