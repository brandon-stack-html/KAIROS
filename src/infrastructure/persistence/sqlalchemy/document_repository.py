"""SqlAlchemyDocumentRepository."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.document.document import Document
from src.domain.document.repository import IDocumentRepository
from src.domain.shared.document_id import DocumentId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyDocumentRepository(
    SqlAlchemyRepository[Document], IDocumentRepository
):
    _entity_class = Document

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def save(self, document: Document) -> None:
        await self._session.merge(document)

    async def find_by_id(self, document_id: DocumentId) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_org(self, org_id: OrganizationId) -> list[Document]:
        stmt = select(Document).where(
            Document.org_id == org_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_project(self, project_id: ProjectId) -> list[Document]:
        stmt = select(Document).where(
            Document.project_id == project_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, document_id: DocumentId) -> None:
        stmt = delete(Document).where(
            Document.id == document_id  # type: ignore[attr-defined]
        )
        await self._session.execute(stmt)
