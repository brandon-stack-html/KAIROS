from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteMessageCommand:
    message_id: str
    requester_id: str  # must match message.sender_id
