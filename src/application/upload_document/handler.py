from src.application.shared.file_storage import IFileStorage
from src.application.upload_document.command import UploadDocumentCommand
from src.application.upload_document.ports import IDocumentUnitOfWork
from src.domain.document.document import Document
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.user.user import UserId


class UploadDocumentHandler:
    def __init__(self, uow: IDocumentUnitOfWork, file_storage: IFileStorage) -> None:
        self._uow = uow
        self._file_storage = file_storage

    async def handle(self, command: UploadDocumentCommand) -> Document:
        storage_path = await self._file_storage.save(
            command.file_content, command.filename
        )

        document = Document.create(
            org_id=OrganizationId.from_str(command.org_id),
            project_id=ProjectId.from_str(command.project_id)
            if command.project_id
            else None,
            uploaded_by=UserId(command.uploaded_by),
            filename=command.filename,
            file_type=command.file_type,
            file_size_bytes=len(command.file_content),
            storage_path=storage_path,
        )

        async with self._uow:
            await self._uow.documents.save(document)

        return document
