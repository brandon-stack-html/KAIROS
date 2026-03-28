from dataclasses import dataclass


@dataclass(frozen=True)
class SendMessageCommand:
    conversation_id: str
    sender_id: str
    content: str
