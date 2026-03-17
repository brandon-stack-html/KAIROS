"""AbstractPasswordHasher — application-level port.

Hashing is a side-effect-free operation, but it depends on a crypto
library (passlib/bcrypt) which is an infrastructure concern. We define
the interface here so use-case handlers stay infrastructure-agnostic.
"""
from abc import ABC, abstractmethod


class AbstractPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain: str) -> str: ...

    @abstractmethod
    def verify(self, plain: str, hashed: str) -> bool: ...
