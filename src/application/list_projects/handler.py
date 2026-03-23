from src.application.create_project.ports import IProjectUnitOfWork
from src.application.list_projects.command import ListProjectsCommand
from src.domain.project.project import Project
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class ListProjectsHandler:
    def __init__(self, uow: IProjectUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListProjectsCommand) -> list[Project]:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)

            if command.org_id is not None:
                org_id = OrganizationId.from_str(command.org_id)
                return await self._uow.projects.find_by_org(org_id, tenant_id)

            user_id = UserId(command.user_id)
            return await self._uow.projects.find_by_user_orgs(user_id, tenant_id)
