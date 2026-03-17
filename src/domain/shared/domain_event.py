from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base for all domain events.

    kw_only=True lets child events declare non-default fields without
    running into the "non-default after default" dataclass restriction.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
