"""IUserRepository — DRIVEN PORT.

Defined in the domain layer so that the domain dictates the contract;
infrastructure implements it.
"""

from abc import ABC, abstractmethod

from src.domain.user.user import User, UserEmail, UserId


class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def find_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: UserEmail) -> User | None: ...

    @abstractmethod
    async def exists_by_email(self, email: UserEmail) -> bool: ...
