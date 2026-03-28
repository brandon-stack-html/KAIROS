from src.application.delete_document.command import DeleteDocumentCommand
from src.application.delete_document.ports import IDeleteDocumentUnitOfWork
from src.application.shared.file_storage import IFileStorage
from src.domain.document.errors import DocumentNotFoundError
from src.domain.organization.errors import (
    InsufficientRoleError,
    OrganizationNotFoundError,
)
from src.domain.shared.document_id import DocumentId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class DeleteDocumentHandler:
    def __init__(
        self, uow: IDeleteDocumentUnitOfWork, file_storage: IFileStorage
    ) -> None:
        self._uow = uow
        self._file_storage = file_storage

    async def handle(self, command: DeleteDocumentCommand) -> None:
        async with self._uow:
            doc_id = DocumentId.from_str(command.document_id)
            document = await self._uow.documents.find_by_id(doc_id)
            if document is None:
                raise DocumentNotFoundError(command.document_id)

            requester_id = UserId(command.requester_id)

            # Allow uploader to delete their own document
            if document.uploaded_by != requester_id:
                # Check if requester is OWNER or ADMIN in the org
                org = await self._uow.organizations.find_by_id(
                    document.org_id, TenantId.from_str(command.tenant_id)
                )
                if org is None:
                    raise OrganizationNotFoundError(document.org_id.value)

                membership = org._find_membership(requester_id)
                if membership is None or membership.role not in (Role.OWNER, Role.ADMIN):
                    raise InsufficientRoleError(
                        "Only document owners, OWNER or ADMIN can delete documents."
                    )

            storage_path = document.storage_path
            await self._uow.documents.delete(doc_id)

        # Delete from storage OUTSIDE the UoW (after commit)
        await self._file_storage.delete(storage_path)
