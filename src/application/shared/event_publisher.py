from abc import ABC, abstractmethod

from src.domain.shared.domain_event import DomainEvent


class AbstractEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None: ...

    async def publish_all(self, events: list[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
