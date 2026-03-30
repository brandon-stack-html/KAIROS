"""OpenRouterAiService — generates AI summaries via the OpenRouter API.

Docs: https://openrouter.ai/docs

Retry: 2 additional attempts on 5xx responses, 1-second backoff.
Timeout: 15 seconds per attempt.
"""

import asyncio

import httpx
import structlog

from src.application.shared.ai_service import IAiSummaryService
from src.application.shared.errors import AiServiceError
from src.domain.deliverable.deliverable import Deliverable

logger = structlog.get_logger()

_API_URL = "https://openrouter.ai/api/v1/chat/completions"
_MAX_ATTEMPTS = 3
_RETRY_BACKOFF_S = 1.0
_TIMEOUT_S = 15.0


def _build_prompt(project_name: str, deliverables: list[Deliverable]) -> str:
    lines = [f"Proyecto: {project_name}", "", "Entregables:"]
    if deliverables:
        for d in deliverables:
            lines.append(f"  - {d.title} [{d.status.value}]")
    else:
        lines.append("  (sin entregables registrados)")
    lines += [
        "",
        "Genera un resumen ejecutivo en español, máximo 3 párrafos, "
        "orientado al cliente (sin tecnicismos). "
        "Describe el estado general del proyecto y el avance de los entregables.",
    ]
    return "\n".join(lines)


class OpenRouterAiService(IAiSummaryService):
    def __init__(self, api_key: str, model: str, frontend_url: str) -> None:
        self._api_key = api_key
        self._model = model
        self._frontend_url = frontend_url

    async def _call_openrouter(
        self, messages: list[dict], context: str = "unknown"
    ) -> str:
        """Call the OpenRouter API with retry logic.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context: Description of what is being generated (for logging)

        Returns:
            The AI-generated response content

        Raises:
            AiServiceError: If all retry attempts fail
        """
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": 500,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._frontend_url,
        }

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                    response = await client.post(
                        _API_URL, json=payload, headers=headers
                    )

                if response.status_code < 500:
                    response.raise_for_status()
                    data = response.json()
                    return data["choices"][0]["message"]["content"]

                logger.warning(
                    "ai.openrouter_5xx",
                    attempt=attempt,
                    status=response.status_code,
                    context=context,
                )
            except httpx.TimeoutException:
                logger.warning(
                    "ai.openrouter_timeout", attempt=attempt, context=context
                )

            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_RETRY_BACKOFF_S)

        logger.error("ai.openrouter_failed", context=context)
        raise AiServiceError(
            f"AI service failed ({context}) after {_MAX_ATTEMPTS} attempts."
        )

    async def generate_project_update(
        self,
        project_name: str,
        deliverables: list[Deliverable],
    ) -> str:
        prompt = _build_prompt(project_name, deliverables)
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente de comunicación para freelancers. "
                    "Redactas actualizaciones de proyecto claras y profesionales "
                    "destinadas a clientes no técnicos."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        return await self._call_openrouter(messages, context=f"project_update:{project_name}")

    async def generate(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        return await self._call_openrouter(messages, context="generate_prompt")
