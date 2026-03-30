"""GenerateDeliverableFeedbackHandler — generates AI-structured feedback for deliverables."""

from src.application.generate_deliverable_feedback.command import (
    GenerateDeliverableFeedbackCommand,
)
from src.application.shared.ai_service import IAiSummaryService
from src.application.submit_deliverable.ports import IDeliverableUnitOfWork
from src.domain.deliverable.deliverable import Deliverable
from src.domain.deliverable.errors import DeliverableNotFoundError
from src.domain.project.project import Project
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.tenant_id import TenantId


def _build_feedback_prompt(
    deliverable: Deliverable, project: Project, feedback_text: str
) -> str:
    """Build a prompt for AI to structure feedback into actionable items.

    Args:
        deliverable: The deliverable being reviewed
        project: The project containing the deliverable
        feedback_text: Raw feedback from the reviewer

    Returns:
        A prompt string for the AI model
    """
    return f"""You are a project management assistant helping structure client feedback for a freelancer.

Project: {project.name}
Deliverable: {deliverable.title}
Deliverable URL: {deliverable.url_link}
Current status: {deliverable.status.value}

The client provided this feedback:
"{feedback_text}"

Generate a structured feedback response in JSON format with EXACTLY this structure (no additional fields):
{{
  "items": [
    {{
      "what": "specific change needed",
      "priority": "high" | "medium" | "low",
      "suggestion": "actionable suggestion for the freelancer"
    }}
  ],
  "summary": "one-sentence summary of all changes needed"
}}

Rules:
- Extract each distinct change request as a separate item
- Be specific and actionable — avoid vague language
- Prioritize based on impact: visual/UX issues = high, text changes = medium, nice-to-haves = low
- Keep suggestions practical — what exactly should the freelancer do
- Return ONLY the JSON, no markdown fences, no preamble, no explanation"""


class GenerateDeliverableFeedbackHandler:
    """Generate structured AI feedback for a deliverable review."""

    def __init__(
        self, uow: IDeliverableUnitOfWork, ai_service: IAiSummaryService
    ) -> None:
        self._uow = uow
        self._ai = ai_service

    async def handle(self, command: GenerateDeliverableFeedbackCommand) -> str:
        """Generate AI-structured feedback for a deliverable.

        Args:
            command: The feedback generation command

        Returns:
            JSON string with structured feedback items

        Raises:
            DeliverableNotFoundError: If the deliverable does not exist
        """
        # Load deliverable and project inside UoW
        async with self._uow:
            deliverable_id = DeliverableId.from_str(command.deliverable_id)
            tenant_id = TenantId.from_str(command.tenant_id)

            deliverable = await self._uow.deliverables.find_by_id(
                deliverable_id, tenant_id
            )
            if deliverable is None:
                raise DeliverableNotFoundError(command.deliverable_id)

            project = await self._uow.projects.find_by_id(
                deliverable.project_id, tenant_id
            )
            # Note: project should exist if deliverable exists (FK constraint)
            # but we trust the DB constraint here

        # UoW closed — AI call outside transaction
        prompt = _build_feedback_prompt(deliverable, project, command.feedback_text)
        ai_response = await self._ai.generate(prompt)

        return ai_response
