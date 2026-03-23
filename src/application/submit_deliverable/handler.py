from src.application.submit_deliverable.command import SubmitDeliverableCommand
from src.application.submit_deliverable.ports import IDeliverableUnitOfWork
from src.domain.deliverable.deliverable import Deliverable
from src.domain.project.errors import ProjectNotFoundError
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class SubmitDeliverableHandler:
    def __init__(self, uow: IDeliverableUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: SubmitDeliverableCommand) -> Deliverable:
        """Returns the created Deliverable."""
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            project_id = ProjectId.from_str(command.project_id)

            project = await self._uow.projects.find_by_id(project_id, tenant_id)
            if project is None:
                raise ProjectNotFoundError(command.project_id)

            deliverable = Deliverable.create(
                title=command.title,
                url_link=command.url_link,
                project_id=project_id,
                tenant_id=tenant_id,
                submitted_by=command.submitter_id,
            )

            await self._uow.deliverables.save(deliverable)

        return deliverable
