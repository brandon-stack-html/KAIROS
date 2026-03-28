from src.application.list_documents.command import ListDocumentsCommand
from src.application.upload_document.ports import IDocumentUnitOfWork
from src.domain.document.document import Document
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


class ListDocumentsHandler:
    def __init__(self, uow: IDocumentUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListDocumentsCommand) -> list[Document]:
        async with self._uow:
            if command.project_id is not None:
                return await self._uow.documents.find_by_project(
                    ProjectId.from_str(command.project_id)
                )
            return await self._uow.documents.find_by_org(
                OrganizationId.from_str(command.org_id)  # type: ignore[arg-type]
            )
