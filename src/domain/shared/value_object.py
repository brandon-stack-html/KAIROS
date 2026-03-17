from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    nombre:str
    UUID:int
    email:str
    phone:int
    

    """Base class for value objects. Immutable; equality is by value."""
    pass
