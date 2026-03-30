"""Port for AI summary generation — implemented by infrastructure adapters."""

from abc import ABC, abstractmethod

from src.domain.deliverable.deliverable import Deliverable


class IAiSummaryService(ABC):
    @abstractmethod
    async def generate_project_update(
        self,
        project_name: str,
        deliverables: list[Deliverable],
    ) -> str: ...

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response from an arbitrary prompt.

        Args:
            prompt: The user prompt to send to the AI model

        Returns:
            The AI-generated response as a string

        Raises:
            AiServiceError: If the AI service fails after retries
        """
        ...
