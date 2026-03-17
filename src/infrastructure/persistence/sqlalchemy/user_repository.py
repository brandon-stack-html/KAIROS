from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user.repository import IUserRepository
from src.domain.user.user import User, UserEmail, UserId


class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        self._session.add(user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def find_by_email(self, email: UserEmail) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: UserEmail) -> bool:
        result = await self._session.execute(
            select(User.id).where(User.email == email).limit(1)
        )
        return result.first() is not None
