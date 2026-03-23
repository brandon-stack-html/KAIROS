import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class DeliverableId(ValueObject):
    """Immutable identifier for a deliverable."""

    value: str

    @classmethod
    def generate(cls) -> "DeliverableId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "DeliverableId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
