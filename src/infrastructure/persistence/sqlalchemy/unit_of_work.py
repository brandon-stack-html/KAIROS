from types import TracebackType
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.register_user.ports import IUserUnitOfWork
from src.infrastructure.persistence.sqlalchemy.user_repository import (
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(IUserUnitOfWork):
    """Manages a single AsyncSession per unit of work.

    Usage (handled automatically by the async context manager):
        async with uow:
            user = await uow.users.find_by_email(email)
            ...
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session: AsyncSession = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
