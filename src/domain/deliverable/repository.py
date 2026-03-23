"""Driven ports for the Deliverable bounded context."""

from abc import ABC, abstractmethod

from src.domain.deliverable.deliverable import Deliverable
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class IDeliverableRepository(ABC):
    @abstractmethod
    async def save(self, deliverable: Deliverable) -> None: ...

    @abstractmethod
    async def find_by_id(
        self, deliverable_id: DeliverableId, tenant_id: TenantId
    ) -> Deliverable | None: ...

    @abstractmethod
    async def find_by_project(
        self, project_id: ProjectId, tenant_id: TenantId
    ) -> list[Deliverable]: ...
