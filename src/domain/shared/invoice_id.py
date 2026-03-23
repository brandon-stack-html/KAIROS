import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class InvoiceId(ValueObject):
    """Immutable identifier for an invoice."""

    value: str

    @classmethod
    def generate(cls) -> "InvoiceId":
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "InvoiceId":
        return cls(value=value)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)
