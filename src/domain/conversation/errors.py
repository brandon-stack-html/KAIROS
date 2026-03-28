from src.domain.shared.errors import DomainError, EntityNotFoundError


class ConversationNotFoundError(EntityNotFoundError):
    def __init__(self, conversation_id: str) -> None:
        super().__init__(f"Conversation '{conversation_id}' not found.")


class InvalidConversationTypeError(DomainError):
    pass
