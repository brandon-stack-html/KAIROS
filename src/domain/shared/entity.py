from abc import ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

TId = TypeVar("TId")


@dataclass(eq=False)
class Entity(ABC, Generic[TId]):
    id: TId

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
