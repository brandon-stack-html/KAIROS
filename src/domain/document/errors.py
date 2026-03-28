from src.domain.shared.errors import DomainError, EntityNotFoundError


class DocumentNotFoundError(EntityNotFoundError):
    def __init__(self, document_id: str) -> None:
        super().__init__(f"Document '{document_id}' not found.")


class FileTooLargeError(DomainError):
    pass


class InvalidFileTypeError(DomainError):
    pass
