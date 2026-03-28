from abc import ABC, abstractmethod

from src.domain.document.document import Document
from src.domain.shared.document_id import DocumentId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


class IDocumentRepository(ABC):
    @abstractmethod
    async def save(self, document: Document) -> None: ...

    @abstractmethod
    async def find_by_id(self, document_id: DocumentId) -> Document | None: ...

    @abstractmethod
    async def find_by_org(self, org_id: OrganizationId) -> list[Document]: ...

    @abstractmethod
    async def find_by_project(self, project_id: ProjectId) -> list[Document]: ...

    @abstractmethod
    async def delete(self, document_id: DocumentId) -> None: ...
