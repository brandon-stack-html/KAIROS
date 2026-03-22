"""Shared pytest fixtures for all test suites.

Strategy:
- Use SQLite in-memory via aiosqlite — no external services needed.
- Each test function gets a fresh, isolated database (function-scoped session).
- The imperative mappers are registered once per test session (idempotent).
- An AsyncClient wrapping the FastAPI app is provided for integration tests.
- InMemoryEmailSender is shared between the client fixture and test functions
  so email assertions can be made after HTTP calls.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.persistence.sqlalchemy.database import metadata

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ── Rate limiter reset (function-scoped — prevents cross-test leakage) ────────

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear the in-memory rate limiter storage before each test."""
    from src.infrastructure.api.rate_limiter import limiter
    limiter._storage.reset()
    yield


# ── Mappers (session-scoped — registering twice would raise) ──────────────────

@pytest.fixture(scope="session", autouse=True)
def register_mappers():
    from src.infrastructure.persistence.sqlalchemy.mappers.invitation_mapper import (
        start_mappers as start_invitation_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.organization_mapper import (
        start_mappers as start_organization_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.refresh_token_mapper import (
        start_mappers as start_refresh_token_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.tenant_mapper import (
        start_mappers as start_tenant_mappers,
    )
    from src.infrastructure.persistence.sqlalchemy.mappers.user_mapper import (
        start_mappers as start_user_mappers,
    )

    start_tenant_mappers()        # tenants first — users has FK to tenants
    start_user_mappers()
    start_refresh_token_mappers() # depends on users
    start_organization_mappers()  # depends on tenants + users
    start_invitation_mappers()    # depends on organizations + users


# ── In-memory database ────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_engine():
    """Fresh SQLite in-memory engine per test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session_factory(test_engine):
    """Session factory bound to the test in-memory engine."""
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(test_session_factory) -> AsyncSession:
    """Async SQLite in-memory session, rolled back after each test."""
    async with test_session_factory() as session:
        yield session


# ── Email sender (in-memory for assertions) ───────────────────────────────────

@pytest.fixture
def email_sender():
    """Fresh InMemoryEmailSender per test — shared with the client fixture."""
    from src.infrastructure.persistence.in_memory.email_sender import InMemoryEmailSender
    return InMemoryEmailSender()


# ── FastAPI test client ───────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
    test_session_factory,
    email_sender,
) -> AsyncClient:
    """Async HTTP client with all UoW dependencies overridden to use the test DB."""
    from src.application.accept_invitation.handler import AcceptInvitationHandler
    from src.application.change_member_role.handler import ChangeMemberRoleHandler
    from src.application.create_organization.handler import CreateOrganizationHandler
    from src.application.invite_member.handler import InviteMemberHandler
    from src.application.list_organizations.handler import ListOrganizationsHandler
    from src.application.login_user.handler import LoginUserHandler
    from src.application.logout_user.handler import LogoutHandler
    from src.application.refresh_token.handler import RefreshTokenHandler
    from src.application.register_user.handler import RegisterUserHandler
    from src.application.remove_member.handler import RemoveMemberHandler
    from src.infrastructure.api.main import app
    from src.infrastructure.config.container import (
        get_accept_invitation_handler,
        get_change_member_role_handler,
        get_create_organization_handler,
        get_invite_member_handler,
        get_list_organizations_handler,
        get_login_user_handler,
        get_logout_handler,
        get_refresh_token_handler,
        get_register_user_handler,
        get_remove_member_handler,
    )
    from src.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
    from src.infrastructure.security.jwt_handler import JwtTokenGenerator
    from src.infrastructure.security.password_hasher import BcryptPasswordHasher

    _hasher = BcryptPasswordHasher()
    _token_generator = JwtTokenGenerator()

    def _uow():
        return SqlAlchemyUnitOfWork(session_factory=test_session_factory)

    def override_get_register_user_handler():
        return RegisterUserHandler(
            uow=_uow(), password_hasher=_hasher, email_sender=email_sender
        )

    def override_get_login_user_handler():
        return LoginUserHandler(uow=_uow(), password_hasher=_hasher, token_generator=_token_generator)

    def override_get_refresh_token_handler():
        return RefreshTokenHandler(uow=_uow(), token_generator=_token_generator)

    def override_get_logout_handler():
        return LogoutHandler(uow=_uow())

    def override_get_create_organization_handler():
        return CreateOrganizationHandler(uow=_uow())

    def override_get_invite_member_handler():
        return InviteMemberHandler(uow=_uow(), email_sender=email_sender)

    def override_get_accept_invitation_handler():
        return AcceptInvitationHandler(uow=_uow())

    def override_get_remove_member_handler():
        return RemoveMemberHandler(uow=_uow())

    def override_get_change_member_role_handler():
        return ChangeMemberRoleHandler(uow=_uow())

    def override_get_list_organizations_handler():
        return ListOrganizationsHandler(uow=_uow())

    app.dependency_overrides[get_register_user_handler] = override_get_register_user_handler
    app.dependency_overrides[get_login_user_handler] = override_get_login_user_handler
    app.dependency_overrides[get_refresh_token_handler] = override_get_refresh_token_handler
    app.dependency_overrides[get_logout_handler] = override_get_logout_handler
    app.dependency_overrides[get_create_organization_handler] = override_get_create_organization_handler
    app.dependency_overrides[get_invite_member_handler] = override_get_invite_member_handler
    app.dependency_overrides[get_accept_invitation_handler] = override_get_accept_invitation_handler
    app.dependency_overrides[get_remove_member_handler] = override_get_remove_member_handler
    app.dependency_overrides[get_change_member_role_handler] = override_get_change_member_role_handler
    app.dependency_overrides[get_list_organizations_handler] = override_get_list_organizations_handler

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
