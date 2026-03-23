"""AbstractRefreshTokenStore — driven port for refresh token persistence.

The application layer defines this interface; infrastructure provides
concrete implementations (SQLAlchemy, in-memory for tests, Redis, etc.).
"""

from abc import ABC, abstractmethod

from src.domain.shared.refresh_token import RefreshToken
from src.domain.user.user import UserId


class AbstractRefreshTokenStore(ABC):
    @abstractmethod
    async def save(self, token: RefreshToken) -> None:
        """Persist a new or updated refresh token."""
        ...

    @abstractmethod
    async def find_by_token(self, token: str) -> RefreshToken | None:
        """Return the RefreshToken for the given UUID string, or None."""
        ...

    @abstractmethod
    async def revoke(self, token: str) -> None:
        """Mark a single token as revoked. No-op if token does not exist."""
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UserId) -> None:
        """Revoke every active refresh token belonging to user_id."""
        ...
