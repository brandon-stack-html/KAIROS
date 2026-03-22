"""ResendEmailSender — sends transactional email via the Resend API.

Docs: https://resend.com/docs/api-reference/emails/send-email

Retry: 2 additional attempts on 5xx responses, 1-second backoff.
Timeout: 10 seconds per attempt.
"""
import asyncio

import httpx
import structlog

from src.application.shared.email_sender import AbstractEmailSender, EmailMessage
from src.application.shared.errors import EmailConfigurationError

logger = structlog.get_logger()

_RESEND_API_URL = "https://api.resend.com/emails"
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_S = 1.0
_TIMEOUT_S = 10.0


class ResendEmailSender(AbstractEmailSender):
    def __init__(self, api_key: str, default_from: str) -> None:
        if not api_key:
            raise EmailConfigurationError(
                "RESEND_API_KEY is not configured. "
                "Set it in your .env file or environment variables."
            )
        self._api_key = api_key
        self._default_from = default_from

    async def send(self, message: EmailMessage) -> None:
        payload = {
            "from": message.from_email or self._default_from,
            "to": [message.to],
            "subject": message.subject,
            "html": message.html_body,
            "text": message.text_body,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                    response = await client.post(
                        _RESEND_API_URL, json=payload, headers=headers
                    )

                if response.status_code < 500:
                    response.raise_for_status()
                    logger.info("email.sent", to=message.to, subject=message.subject)
                    return

                # 5xx — retry
                logger.warning(
                    "email.resend_5xx",
                    attempt=attempt,
                    status=response.status_code,
                    to=message.to,
                )
            except httpx.TimeoutException:
                logger.warning("email.resend_timeout", attempt=attempt, to=message.to)

            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_RETRY_BACKOFF_S)

        logger.error("email.resend_failed", to=message.to, subject=message.subject)
        raise RuntimeError(
            f"Failed to send email to {message.to} after {_MAX_ATTEMPTS} attempts."
        )
