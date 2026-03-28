"""Message aggregate root.

Domain rules:
- Content must be 1–4000 characters (stripped).
- Only the sender can delete their own message (enforced at handler level).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.message.errors import InvalidMessageContentError
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.message_id import MessageId
from src.domain.user.user import UserId

_MAX_CONTENT = 4000


@dataclass(eq=False)
class Message(AggregateRoot):
    """Message aggregate root."""

    id: MessageId
    conversation_id: ConversationId
    sender_id: UserId
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate_content(self.content)

    @classmethod
    def create(
        cls,
        conversation_id: ConversationId,
        sender_id: UserId,
        content: str,
    ) -> "Message":
        content = content.strip()
        cls._validate_content(content)
        return cls(
            id=MessageId.generate(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
        )

    @staticmethod
    def _validate_content(content: str) -> None:
        if not (1 <= len(content) <= _MAX_CONTENT):
            raise InvalidMessageContentError(content)
