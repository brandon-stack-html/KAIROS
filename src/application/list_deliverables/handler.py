from src.application.list_deliverables.command import ListDeliverablesCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.deliverable.deliverable import Deliverable
from src.domain.project.errors import ProjectNotFoundError
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class ListDeliverablesHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListDeliverablesCommand) -> list[Deliverable]:
        async with self._uow:
            project_id = ProjectId.from_str(command.project_id)
            tenant_id = TenantId.from_str(command.tenant_id)
            project = await self._uow.projects.find_by_id(project_id, tenant_id)
            if project is None:
                raise ProjectNotFoundError(command.project_id)
            return await self._uow.deliverables.find_by_project(project_id, tenant_id)
