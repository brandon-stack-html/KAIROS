"""Integration tests — multi-tenant isolation.

Tests run against SQLite in-memory (same as all integration tests).
Isolation is enforced at the application layer (repository WHERE clauses).
PostgreSQL RLS provides an additional DB-level guarantee in production.

Scenarios:
  1. User registered under tenant_A is NOT visible when querying as tenant_B.
  2. User is visible when querying under their own tenant.
  3. Registering via HTTP injects tenant_id correctly from the request body.
  4. TenantMiddleware returns 401 on protected routes without a valid tenant claim.
  5. Login returns a JWT that contains the 'tid' claim.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.handler import RegisterUserHandler
from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.tenant import Tenant
from src.domain.user.user import UserEmail
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)
from src.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.persistence.sqlalchemy.user_repository import (
    SqlAlchemyUserRepository,
)
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

_hasher = BcryptPasswordHasher()


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _create_tenant(session: AsyncSession, name: str, slug: str) -> Tenant:
    repo = SqlAlchemyTenantRepository(session)
    tenant = Tenant.provision(name=name, slug=slug)
    await repo.save(tenant)
    await session.commit()
    return tenant


async def _register_user(
    session_factory,
    email: str,
    tenant_id: str,
) -> str:
    """Register a user and return their id."""
    uow = SqlAlchemyUnitOfWork(session_factory=session_factory, tenant_id=tenant_id)
    handler = RegisterUserHandler(uow=uow, password_hasher=_hasher)
    return await handler.handle(
        RegisterUserCommand(
            email=email,
            name="Test User",
            password="Password1!",
            tenant_id=tenant_id,
        )
    )


# ── Test 1: Cross-tenant isolation ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_not_visible_across_tenants(db_session: AsyncSession):
    """A user registered under tenant_A must NOT be returned when querying as tenant_B."""
    tenant_a = await _create_tenant(db_session, "Tenant A", "tenant-a")
    tenant_b = await _create_tenant(db_session, "Tenant B", "tenant-b")

    # Register user under tenant_A
    repo_a = SqlAlchemyUserRepository(db_session, tenant_id=tenant_a.id.value)
    from src.domain.user.user import User, UserEmail, UserName
    user = User.register(
        email=UserEmail("alice@tenant-a.com"),
        name=UserName("Alice"),
        hashed_password=_hasher.hash("Password1!"),
        tenant_id=tenant_a.id,
    )
    await repo_a.save(user)
    await db_session.commit()

    # Query as tenant_B — should NOT see tenant_A's user
    repo_b = SqlAlchemyUserRepository(db_session, tenant_id=tenant_b.id.value)
    found = await repo_b.find_by_email(UserEmail("alice@tenant-a.com"))
    assert found is None, "User from tenant_A leaked into tenant_B query"


# ── Test 2: Same-tenant visibility ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_user_visible_within_own_tenant(db_session: AsyncSession):
    """A user is visible when queried within the same tenant context."""
    tenant = await _create_tenant(db_session, "Visible Corp", "visible-corp")

    from src.domain.user.user import User, UserEmail, UserName
    user = User.register(
        email=UserEmail("bob@visible-corp.com"),
        name=UserName("Bob"),
        hashed_password=_hasher.hash("Password1!"),
        tenant_id=tenant.id,
    )
    repo = SqlAlchemyUserRepository(db_session, tenant_id=tenant.id.value)
    await repo.save(user)
    await db_session.commit()

    found = await repo.find_by_email(UserEmail("bob@visible-corp.com"))
    assert found is not None
    assert found.tenant_id == tenant.id


# ── Test 3: HTTP registration injects tenant_id ───────────────────────────────

@pytest.mark.asyncio
async def test_http_registration_stores_tenant_id(client: AsyncClient):
    """POST /api/v1/users accepts tenant_id and returns 201.

    Full end-to-end persistence is covered by test_login_jwt_contains_tenant_id,
    which registers + logs in and asserts the 'tid' claim in the returned JWT.
    Here we verify the API contract: the endpoint accepts tenant_id and responds
    correctly, including validating the UUID format.
    """
    valid_tenant_id = str(TenantId.generate().value)

    # Valid registration
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "carol@http-corp.com",
            "name": "Carol",
            "password": "Password1!",
            "tenant_id": valid_tenant_id,
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "carol@http-corp.com"

    # Invalid tenant_id format is rejected at schema validation (422)
    response_bad = await client.post(
        "/api/v1/users/",
        json={
            "email": "bad@http-corp.com",
            "name": "Bad",
            "password": "Password1!",
            "tenant_id": "not-a-uuid",
        },
    )
    assert response_bad.status_code == 422


# ── Test 4: TenantMiddleware blocks protected routes without tid ───────────────

@pytest.mark.asyncio
async def test_protected_route_without_tenant_returns_401(client: AsyncClient):
    """A protected route with a JWT missing the 'tid' claim returns 401."""
    import jwt as pyjwt

    from src.infrastructure.config.settings import settings

    # Forge a token WITHOUT the 'tid' claim
    import datetime
    token = pyjwt.encode(
        {
            "sub": "00000000-0000-4000-8000-000000000001",
            "email": "test@test.com",
            "iat": datetime.datetime.now(datetime.UTC),
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5),
            # 'tid' intentionally omitted
        },
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    # Hit a fictional protected endpoint (any non-public path)
    response = await client.get(
        "/api/v1/protected-example",
        headers={"Authorization": f"Bearer {token}"},
    )
    # 401 from TenantMiddleware (before routing even happens)
    assert response.status_code == 401


# ── Test 5: Login JWT contains 'tid' claim ────────────────────────────────────

@pytest.mark.asyncio
async def test_login_jwt_contains_tenant_id(
    db_session: AsyncSession, client: AsyncClient
):
    """Login response JWT must contain the user's tenant_id as the 'tid' claim."""
    import jwt as pyjwt

    from src.infrastructure.config.settings import settings

    tenant = await _create_tenant(db_session, "Login Corp", "login-corp")

    # Register first
    await client.post(
        "/api/v1/users/",
        json={
            "email": "dave@login-corp.com",
            "name": "Dave",
            "password": "Password1!",
            "tenant_id": tenant.id.value,
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "dave@login-corp.com", "password": "Password1!"},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    payload = pyjwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

    assert "tid" in payload, "JWT is missing 'tid' claim"
    assert payload["tid"] == tenant.id.value
