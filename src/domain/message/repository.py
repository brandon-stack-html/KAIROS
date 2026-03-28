"""Driven port for the Message bounded context."""

from abc import ABC, abstractmethod

from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.message_id import MessageId


class IMessageRepository(ABC):
    @abstractmethod
    async def save(self, message: Message) -> None: ...

    @abstractmethod
    async def find_by_id(self, message_id: MessageId) -> Message | None: ...

    @abstractmethod
    async def find_by_conversation(
        self,
        conversation_id: ConversationId,
        *,
        page: int,
        limit: int,
    ) -> list[Message]: ...

    @abstractmethod
    async def delete(self, message_id: MessageId) -> None: ...
