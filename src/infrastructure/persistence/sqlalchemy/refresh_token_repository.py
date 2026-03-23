"""SqlAlchemyRefreshTokenStore — SQLAlchemy implementation of AbstractRefreshTokenStore."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.shared.refresh_token_store import AbstractRefreshTokenStore
from src.domain.shared.refresh_token import RefreshToken
from src.domain.user.user import UserId


class SqlAlchemyRefreshTokenStore(AbstractRefreshTokenStore):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, token: RefreshToken) -> None:
        """Insert or update a refresh token.

        Uses merge() so that calling save() on a revoke()d token (which is a
        new Python object with the same PK) does an UPDATE rather than INSERT.
        """
        await self._session.merge(token)

    async def find_by_token(self, token: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token == token)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: str) -> None:
        await self._session.execute(
            update(RefreshToken)  # type: ignore[arg-type]
            .where(RefreshToken.token == token)  # type: ignore[attr-defined]
            .values(is_revoked=True)
        )

    async def revoke_all_for_user(self, user_id: UserId) -> None:
        await self._session.execute(
            update(RefreshToken)  # type: ignore[arg-type]
            .where(
                RefreshToken.user_id == user_id,  # type: ignore[attr-defined]
                RefreshToken.is_revoked.is_(False),  # type: ignore[attr-defined]
            )
            .values(is_revoked=True)
        )
