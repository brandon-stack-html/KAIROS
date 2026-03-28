from src.application.download_document.command import DownloadDocumentCommand
from src.application.upload_document.ports import IDocumentUnitOfWork
from src.domain.document.document import Document
from src.domain.document.errors import DocumentNotFoundError
from src.domain.shared.document_id import DocumentId


class DownloadDocumentHandler:
    def __init__(self, uow: IDocumentUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: DownloadDocumentCommand) -> Document:
        async with self._uow:
            document = await self._uow.documents.find_by_id(
                DocumentId.from_str(command.document_id)
            )
            if document is None:
                raise DocumentNotFoundError(command.document_id)
            return document
