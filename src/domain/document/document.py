"""Document aggregate root."""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.document.errors import FileTooLargeError, InvalidFileTypeError
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.document_id import DocumentId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.user.user import UserId

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/zip",
    "text/plain",
}


@dataclass(eq=False)
class Document(AggregateRoot):
    id: DocumentId
    org_id: OrganizationId
    project_id: ProjectId | None
    uploaded_by: UserId
    filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        org_id: OrganizationId,
        project_id: ProjectId | None,
        uploaded_by: UserId,
        filename: str,
        file_type: str,
        file_size_bytes: int,
        storage_path: str,
    ) -> "Document":
        if file_size_bytes > MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File size {file_size_bytes} exceeds maximum of {MAX_FILE_SIZE} bytes."
            )
        if file_type not in ALLOWED_FILE_TYPES:
            raise InvalidFileTypeError(
                f"File type '{file_type}' is not allowed."
            )
        return cls(
            id=DocumentId.generate(),
            org_id=org_id,
            project_id=project_id,
            uploaded_by=uploaded_by,
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            storage_path=storage_path,
        )
