from src.application.get_project.command import GetProjectCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.project.errors import ProjectNotFoundError
from src.domain.project.project import Project
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class GetProjectHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetProjectCommand) -> Project:
        async with self._uow:
            project_id = ProjectId.from_str(command.project_id)
            tenant_id = TenantId.from_str(command.tenant_id)
            project = await self._uow.projects.find_by_id(project_id, tenant_id)
            if project is None:
                raise ProjectNotFoundError(command.project_id)
            return project
