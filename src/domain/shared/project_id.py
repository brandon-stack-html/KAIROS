import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class ProjectId(ValueObject):
    """Immutable identifier for a project."""

    value: str

    @classmethod
    def generate(cls) -> "ProjectId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "ProjectId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
