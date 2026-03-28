from dataclasses import dataclass


@dataclass(frozen=True)
class GetConversationCommand:
    conversation_id: str
