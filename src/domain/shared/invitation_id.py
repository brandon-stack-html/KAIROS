import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class InvitationId(ValueObject):
    """Immutable identifier for an organization invitation."""

    value: str

    @classmethod
    def generate(cls) -> "InvitationId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "InvitationId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
