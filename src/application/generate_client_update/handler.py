from src.application.generate_client_update.command import GenerateClientUpdateCommand
from src.application.generate_client_update.ports import IGenerateClientUpdateUnitOfWork
from src.application.shared.ai_service import IAiSummaryService
from src.domain.project.errors import ProjectNotFoundError
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class GenerateClientUpdateHandler:
    def __init__(
        self,
        uow: IGenerateClientUpdateUnitOfWork,
        ai_service: IAiSummaryService,
    ) -> None:
        self._uow = uow
        self._ai_service = ai_service

    async def handle(self, command: GenerateClientUpdateCommand) -> str:
        # ── INSIDE UoW: fetch from DB ────────────────────────────────────
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            project_id = ProjectId.from_str(command.project_id)

            project = await self._uow.projects.find_by_id(project_id, tenant_id)
            if project is None:
                raise ProjectNotFoundError(command.project_id)

            deliverables = await self._uow.deliverables.find_by_project(
                project.id, project.tenant_id
            )
            # Capture what we need — session closes after this block
            project_name = project.name

        # ── OUTSIDE UoW: AI call (no open DB transaction during HTTP call) ─
        summary = await self._ai_service.generate_project_update(
            project_name, deliverables
        )
        return summary
