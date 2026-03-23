from src.application.create_project.command import CreateProjectCommand
from src.application.create_project.ports import IProjectUnitOfWork
from src.domain.organization.errors import (
    InsufficientRoleError,
    OrganizationNotFoundError,
)
from src.domain.project.project import Project
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class CreateProjectHandler:
    def __init__(self, uow: IProjectUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateProjectCommand) -> Project:
        """Returns the created Project."""
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            org_id = OrganizationId.from_str(command.org_id)
            owner_id = UserId(command.owner_id)

            org = await self._uow.organizations.find_by_id(org_id, tenant_id)
            if org is None:
                raise OrganizationNotFoundError(command.org_id)

            membership = org._find_membership(owner_id)
            if membership is None or membership.role is not Role.OWNER:
                raise InsufficientRoleError("Only an OWNER can create projects.")

            project = Project.create(
                name=command.name,
                description=command.description,
                org_id=org_id,
                tenant_id=tenant_id,
                owner_id=command.owner_id,
            )

            await self._uow.projects.save(project)

        return project
