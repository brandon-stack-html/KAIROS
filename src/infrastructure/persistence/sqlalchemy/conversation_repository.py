"""SqlAlchemyConversationRepository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.conversation.conversation import Conversation
from src.domain.conversation.repository import IConversationRepository
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyConversationRepository(
    SqlAlchemyRepository[Conversation], IConversationRepository
):
    _entity_class = Conversation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def save(self, conversation: Conversation) -> None:
        await self._session.merge(conversation)

    async def find_by_id(
        self, conversation_id: ConversationId
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_org(
        self, org_id: OrganizationId
    ) -> list[Conversation]:
        stmt = select(Conversation).where(
            Conversation.org_id == org_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_project(
        self, project_id: ProjectId
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.project_id == project_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
