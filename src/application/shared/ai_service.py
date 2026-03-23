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
