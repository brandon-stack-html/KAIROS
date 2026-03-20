from sqlalchemy import select

from src.domain.user.repository import IUserRepository
from src.domain.user.user import User, UserEmail, UserId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyUserRepository(SqlAlchemyRepository[User], IUserRepository):
    _entity_class = User

    async def save(self, user: User) -> None:
        await self.add(user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        return await self.get_by_id(user_id)

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
