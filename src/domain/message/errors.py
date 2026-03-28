from src.domain.shared.errors import DomainError, EntityNotFoundError


class MessageNotFoundError(EntityNotFoundError):
    def __init__(self, message_id: str) -> None:
        super().__init__(f"Message '{message_id}' not found.")


class InvalidMessageContentError(DomainError):
    def __init__(self, content: str) -> None:
        length = len(content)
        super().__init__(
            f"Message content must be 1–4000 characters; got {length}."
        )


class MessageNotOwnedError(DomainError):
    def __init__(self) -> None:
        super().__init__("You can only delete your own messages.")
