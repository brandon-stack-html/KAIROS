"""TenantId value object — shared building block for multi-tenancy.

Every aggregate that belongs to a tenant carries a TenantId.
Domain rules enforced here:
- Must be a valid UUID v4 (lowercase canonical form).
- Cannot be empty or None.
"""
import re
import uuid
from dataclasses import dataclass

from src.domain.shared.value_object import ValueObject

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@dataclass(frozen=True)
class TenantId(ValueObject):
    """Immutable identifier for a tenant. Equality is by value."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("TenantId cannot be empty.")
        if not _UUID4_RE.match(self.value.lower()):
            raise ValueError(
                f"TenantId must be a valid UUID v4, got: {self.value!r}"
            )

    @classmethod
    def generate(cls) -> "TenantId":
        """Create a new random TenantId."""
        return cls(value=str(uuid.uuid4()))

    @classmethod
    def from_str(cls, value: str) -> "TenantId":
        """Parse and validate a TenantId from a string."""
        return cls(value=value.lower())

    def __composite_values__(self) -> tuple[str]:
        """Required by SQLAlchemy composite() mapping."""
        return (self.value,)
