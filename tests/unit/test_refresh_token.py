"""Unit tests — RefreshToken value object + use case handlers.

All tests use InMemoryRefreshTokenStore + InMemoryUoW — no DB, no HTTP.
"""

import pytest

from src.application.login_user.ports import ITokenGenerator
from src.application.logout_user.command import LogoutCommand
from src.application.logout_user.handler import LogoutHandler
from src.application.refresh_token.command import RefreshTokenCommand
from src.application.refresh_token.handler import RefreshTokenHandler
from src.application.register_user.ports import IUserUnitOfWork
from src.domain.shared.errors import InvalidRefreshTokenError
from src.domain.shared.refresh_token import RefreshToken
from src.domain.shared.tenant_id import TenantId
from src.domain.user.repository import IUserRepository
from src.domain.user.user import User, UserEmail, UserId, UserName
from src.infrastructure.persistence.in_memory.refresh_token_store import (
    InMemoryRefreshTokenStore,
)

# ── Test doubles ──────────────────────────────────────────────────────────────


class _FakeTokenGenerator(ITokenGenerator):
    def generate(self, user_id: str, email: str, tenant_id: str) -> str:
        return f"access:{user_id}"


class _FakeUserRepository(IUserRepository):
    def __init__(self, user: User | None = None) -> None:
        self._user = user

    async def save(self, user: User) -> None:
        self._user = user

    async def find_by_id(self, user_id: UserId) -> User | None:
        if self._user and self._user.id == user_id:
            return self._user
        return None

    async def find_by_email(self, email: UserEmail) -> User | None:
        if self._user and self._user.email == email:
            return self._user
        return None

    async def exists_by_email(self, email: UserEmail) -> bool:
        return self._user is not None and self._user.email == email


class _FakeUoW(IUserUnitOfWork):
    def __init__(
        self, store: InMemoryRefreshTokenStore, user: User | None = None
    ) -> None:
        self.users = _FakeUserRepository(user)
        self.refresh_tokens = store

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass  # no-op commit/rollback in tests

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_user() -> User:
    return User(
        id=UserId.generate(),
        email=UserEmail("alice@example.com"),
        name=UserName("Alice"),
        hashed_password="hash",
        tenant_id=TenantId.generate(),
    )


def _make_token(
    user: User, *, ttl_days: int = 30, revoked: bool = False
) -> RefreshToken:
    t = RefreshToken.issue(user_id=user.id, tenant_id=user.tenant_id, ttl_days=ttl_days)
    return t.revoke() if revoked else t


# ── Tests: RefreshToken value object ─────────────────────────────────────────


def test_refresh_token_is_not_expired_when_fresh():
    user = _make_user()
    t = _make_token(user)
    assert not t.is_expired()


def test_refresh_token_is_expired_when_ttl_is_zero():
    user = _make_user()
    t = RefreshToken.issue(user_id=user.id, tenant_id=user.tenant_id, ttl_days=0)
    # expires_at = now + 0 days ≈ now, so is_expired() → True immediately
    assert t.is_expired()


def test_revoke_returns_new_instance_with_is_revoked_true():
    user = _make_user()
    t = _make_token(user)
    revoked = t.revoke()
    assert revoked.is_revoked
    assert not t.is_revoked  # original unchanged


# ── Tests: RefreshTokenHandler ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_returns_new_tokens():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    old_token = _make_token(user)
    await store.save(old_token)

    uow = _FakeUoW(store=store, user=user)
    handler = RefreshTokenHandler(uow=uow, token_generator=_FakeTokenGenerator())

    access_token, new_refresh = await handler.handle(
        RefreshTokenCommand(token=old_token.token)
    )

    assert access_token.startswith("access:")
    assert new_refresh != old_token.token


@pytest.mark.asyncio
async def test_refresh_revokes_old_token():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    old_token = _make_token(user)
    await store.save(old_token)

    uow = _FakeUoW(store=store, user=user)
    await RefreshTokenHandler(uow=uow, token_generator=_FakeTokenGenerator()).handle(
        RefreshTokenCommand(token=old_token.token)
    )

    stored = await store.find_by_token(old_token.token)
    assert stored is not None and stored.is_revoked


@pytest.mark.asyncio
async def test_refresh_with_revoked_token_raises():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    revoked = _make_token(user, revoked=True)
    await store.save(revoked)

    uow = _FakeUoW(store=store, user=user)
    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenHandler(
            uow=uow, token_generator=_FakeTokenGenerator()
        ).handle(RefreshTokenCommand(token=revoked.token))


@pytest.mark.asyncio
async def test_refresh_with_expired_token_raises():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    expired = RefreshToken.issue(user_id=user.id, tenant_id=user.tenant_id, ttl_days=0)
    await store.save(expired)

    uow = _FakeUoW(store=store, user=user)
    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenHandler(
            uow=uow, token_generator=_FakeTokenGenerator()
        ).handle(RefreshTokenCommand(token=expired.token))


@pytest.mark.asyncio
async def test_refresh_with_unknown_token_raises():
    user = _make_user()
    store = InMemoryRefreshTokenStore()  # empty

    uow = _FakeUoW(store=store, user=user)
    with pytest.raises(InvalidRefreshTokenError):
        await RefreshTokenHandler(
            uow=uow, token_generator=_FakeTokenGenerator()
        ).handle(RefreshTokenCommand(token="00000000-0000-4000-8000-000000000000"))


# ── Tests: LogoutHandler ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_logout_revokes_token():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    t = _make_token(user)
    await store.save(t)

    await LogoutHandler(uow=_FakeUoW(store=store)).handle(
        LogoutCommand(refresh_token=t.token)
    )

    stored = await store.find_by_token(t.token)
    assert stored is not None and stored.is_revoked


@pytest.mark.asyncio
async def test_logout_is_idempotent():
    user = _make_user()
    store = InMemoryRefreshTokenStore()
    t = _make_token(user)
    await store.save(t)

    handler = LogoutHandler(uow=_FakeUoW(store=store))
    await handler.handle(LogoutCommand(refresh_token=t.token))
    await handler.handle(
        LogoutCommand(refresh_token=t.token)
    )  # second call must not raise
