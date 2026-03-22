"""InMemoryEmailSender — captures sent emails for test assertions."""
from src.application.shared.email_sender import AbstractEmailSender, EmailMessage


class InMemoryEmailSender(AbstractEmailSender):
    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    async def send(self, message: EmailMessage) -> None:
        self.sent.append(message)

    def find_by_to(self, email: str) -> list[EmailMessage]:
        return [m for m in self.sent if m.to == email]

    def clear(self) -> None:
        self.sent.clear()
