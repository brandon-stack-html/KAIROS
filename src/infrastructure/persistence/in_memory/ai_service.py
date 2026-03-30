"""InMemoryAiService — deterministic AI responses for tests and dev fallback."""

from src.application.shared.ai_service import IAiSummaryService
from src.domain.deliverable.deliverable import Deliverable


class InMemoryAiService(IAiSummaryService):
    def __init__(self) -> None:
        self.response: str | None = None  # override for specific test assertions
        self.calls: list[dict] = []  # records each invocation for unit test inspection

    async def generate_project_update(
        self,
        project_name: str,
        deliverables: list[Deliverable],
    ) -> str:
        self.calls.append(
            {"project_name": project_name, "deliverables": list(deliverables)}
        )
        if self.response is not None:
            return self.response
        return (
            f"Resumen del proyecto {project_name}: "
            f"{len(deliverables)} entregable(s) registrado(s)."
        )

    async def generate(self, prompt: str) -> str:
        self.calls.append({"prompt": prompt})
        if self.response is not None:
            return self.response
        return '{"items": [], "summary": "stub response"}'
