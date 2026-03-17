from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .entity import Entity
from .domain_event import DomainEvent

TId = TypeVar("TId")


@dataclass(eq=False)
class AggregateRoot(Entity[TId], Generic[TId]):
    _domain_events: list[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def add_domain_event(self, event: DomainEvent) -> None:
        # Guard: SQLAlchemy imperative mapping bypasses __init__ on DB load,
        # so _domain_events may not be initialised for reconstructed objects.
        if not hasattr(self, "_domain_events") or self._domain_events is None:
            self._domain_events = []
        self._domain_events.append(event)

    def pull_domain_events(self) -> list[DomainEvent]:
        if not hasattr(self, "_domain_events") or self._domain_events is None:
            self._domain_events = []
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
