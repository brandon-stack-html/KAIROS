from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base class for value objects. Immutable; equality is by value."""
