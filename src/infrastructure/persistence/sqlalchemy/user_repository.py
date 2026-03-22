from sqlalchemy import select

from src.domain.user.repository import IUserRepository
from src.domain.user.user import User, UserEmail, UserId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyUserRepository(SqlAlchemyRepository[User], IUserRepository):
    _entity_class = User

    def __init__(self, session, tenant_id: str | None = None) -> None:
        super().__init__(session)
        self._tenant_id = tenant_id

    # ── Helpers ───────────────────────────────────────────────────────────

    def _tenant_filter(self, stmt):
        """Apply tenant_id WHERE clause when running in a tenant context."""
        if self._tenant_id is not None:
            stmt = stmt.where(User.tenant_id == self._tenant_id)  # type: ignore[attr-defined]
        return stmt

    # ── Port implementation ───────────────────────────────────────────────

    async def save(self, user: User) -> None:
        await self.add(user)

    async def find_by_id(self, user_id: UserId) -> User | None:
        stmt = self._tenant_filter(select(User).where(User.id == user_id))  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: UserEmail) -> User | None:
        stmt = self._tenant_filter(select(User).where(User.email == email))  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: UserEmail) -> bool:
        stmt = self._tenant_filter(
            select(User.id).where(User.email == email).limit(1)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.first() is not None
