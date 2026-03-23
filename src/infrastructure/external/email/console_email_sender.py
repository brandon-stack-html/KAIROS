"""ConsoleEmailSender — prints emails to stdout via structlog.

Use in local development when no real email credentials are available.
"""

import structlog

from src.application.shared.email_sender import AbstractEmailSender, EmailMessage

logger = structlog.get_logger()


class ConsoleEmailSender(AbstractEmailSender):
    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "email.console",
            to=message.to,
            subject=message.subject,
            body=message.text_body,
        )
