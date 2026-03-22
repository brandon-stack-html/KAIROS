"""Integration tests — full auth flow (login → refresh → logout).

Tests run against SQLite in-memory via the test client fixture.
All HTTP handlers are overridden in conftest to use the test session.
"""
import pytest
from httpx import AsyncClient

from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession

# Reusable credentials
_EMAIL = "auth-flow@example.com"
_PASSWORD = "Password1!"
_NAME = "Auth Flow User"


async def _setup_tenant_and_user(
    db_session: AsyncSession, client: AsyncClient
) -> tuple[str, str, str]:
    """Create a tenant, register a user, return (tenant_id, email, password)."""
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(name="Auth Corp", slug="auth-corp")
    await repo.save(tenant)
    await db_session.commit()

    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": _EMAIL,
            "name": _NAME,
            "password": _PASSWORD,
            "tenant_id": str(tenant.id.value),
        },
    )
    assert resp.status_code == 201, resp.text
    return str(tenant.id.value), _EMAIL, _PASSWORD


# ── Test 1: Login returns access_token + refresh_token ───────────────────────

@pytest.mark.asyncio
async def test_login_returns_both_tokens(db_session: AsyncSession, client: AsyncClient):
    """POST /auth/login must return access_token and refresh_token."""
    await _setup_tenant_and_user(db_session, client)

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": _EMAIL, "password": _PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # refresh_token must look like a UUID
    assert len(data["refresh_token"]) == 36


# ── Test 2: Refresh returns new tokens ───────────────────────────────────────

@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(db_session: AsyncSession, client: AsyncClient):
    """POST /auth/refresh must return a new access_token + a NEW refresh_token."""
    await _setup_tenant_and_user(db_session, client)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": _EMAIL, "password": _PASSWORD},
    )
    original_refresh = login_resp.json()["refresh_token"]
    original_access = login_resp.json()["access_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert refresh_resp.status_code == 200, refresh_resp.text
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Refresh token must be rotated (new UUID)
    assert data["refresh_token"] != original_refresh
    # Access token is a JWT string
    assert data["access_token"].count(".") == 2


# ── Test 3: Used refresh token cannot be reused ───────────────────────────────

@pytest.mark.asyncio
async def test_used_refresh_token_returns_401(db_session: AsyncSession, client: AsyncClient):
    """A refresh token already consumed (rotated) must return 401."""
    await _setup_tenant_and_user(db_session, client)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": _EMAIL, "password": _PASSWORD},
    )
    original_refresh = login_resp.json()["refresh_token"]

    # First use — valid
    first_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert first_resp.status_code == 200

    # Second use — must fail (token is now revoked)
    second_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert second_resp.status_code == 401, second_resp.text


# ── Test 4: Logout revokes token, refresh fails afterwards ───────────────────

@pytest.mark.asyncio
async def test_logout_makes_refresh_token_invalid(
    db_session: AsyncSession, client: AsyncClient
):
    """After logout, attempting to use the refresh token must return 401."""
    await _setup_tenant_and_user(db_session, client)

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": _EMAIL, "password": _PASSWORD},
    )
    refresh_token = login_resp.json()["refresh_token"]

    # Logout
    logout_resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 204

    # Token is now revoked — refresh must fail
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401, refresh_resp.text


# ── Test 5: Bad UUID format rejected at schema level ────────────────────────

@pytest.mark.asyncio
async def test_refresh_with_invalid_uuid_returns_422(client: AsyncClient):
    """A non-UUID refresh_token must be rejected by schema validation (422)."""
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-uuid"},
    )
    assert resp.status_code == 422
