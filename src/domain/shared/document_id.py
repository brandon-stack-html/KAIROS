import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class DocumentId(ValueObject):
    value: str

    @classmethod
    def generate(cls) -> "DocumentId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "DocumentId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
