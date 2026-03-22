import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class MembershipId(ValueObject):
    """Immutable identifier for an organization membership."""

    value: str

    @classmethod
    def generate(cls) -> "MembershipId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "MembershipId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
