"""Integration tests — Login error paths.

UserNotFoundError → EntityNotFoundError → 404 (anti-enumeration: same code
for both "user doesn't exist" and "wrong password").
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import provision_tenant, register_user


@pytest.mark.asyncio
async def test_login_wrong_password_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    tid = await provision_tenant(db_session, "Auth Corp", "auth-corp")
    await register_user(client, tid, "user@auth.com")

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "user@auth.com", "password": "WrongPass1!"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_404(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@nowhere.com", "password": "Password1!"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_login_invalid_email_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bad-email", "password": "Password1!"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_fields_returns_422(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_password_too_short_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "ok@test.com", "password": "ab"},
    )
    assert resp.status_code == 422
