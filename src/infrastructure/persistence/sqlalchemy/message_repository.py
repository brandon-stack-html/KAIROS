"""SqlAlchemyMessageRepository."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.message.message import Message
from src.domain.message.repository import IMessageRepository
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.message_id import MessageId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyMessageRepository(
    SqlAlchemyRepository[Message], IMessageRepository
):
    _entity_class = Message

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def save(self, message: Message) -> None:
        await self._session.merge(message)

    async def find_by_id(self, message_id: MessageId) -> Message | None:
        stmt = select(Message).where(
            Message.id == message_id  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_conversation(
        self,
        conversation_id: ConversationId,
        *,
        page: int,
        limit: int,
    ) -> list[Message]:
        offset = (page - 1) * limit
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)  # type: ignore[attr-defined]
            .order_by(Message.created_at)  # type: ignore[attr-defined]
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, message_id: MessageId) -> None:
        stmt = delete(Message).where(
            Message.id == message_id  # type: ignore[attr-defined]
        )
        await self._session.execute(stmt)
