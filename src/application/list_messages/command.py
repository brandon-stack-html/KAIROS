from dataclasses import dataclass


@dataclass(frozen=True)
class ListMessagesCommand:
    conversation_id: str
    page: int = 1
    limit: int = 50
