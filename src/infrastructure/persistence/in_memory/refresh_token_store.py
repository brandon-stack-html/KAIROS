"""InMemoryRefreshTokenStore — in-memory implementation for unit tests.

Stores tokens in a plain dict keyed by token UUID string.
Thread-safety is not a concern in single-threaded async tests.
"""

from dataclasses import replace

from src.application.shared.refresh_token_store import AbstractRefreshTokenStore
from src.domain.shared.refresh_token import RefreshToken
from src.domain.user.user import UserId


class InMemoryRefreshTokenStore(AbstractRefreshTokenStore):
    def __init__(self) -> None:
        self._store: dict[str, RefreshToken] = {}

    async def save(self, token: RefreshToken) -> None:
        self._store[token.token] = token

    async def find_by_token(self, token: str) -> RefreshToken | None:
        return self._store.get(token)

    async def revoke(self, token: str) -> None:
        existing = self._store.get(token)
        if existing is not None:
            self._store[token] = replace(existing, is_revoked=True)

    async def revoke_all_for_user(self, user_id: UserId) -> None:
        for key, token in self._store.items():
            if token.user_id == user_id and not token.is_revoked:
                self._store[key] = replace(token, is_revoked=True)
