"""Integration tests — PATCH /api/v1/users/me (update profile)."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)

_EMAIL = "profile-test@example.com"
_PASSWORD = "Password1!"
_NAME = "Profile User"


async def _setup(db_session: AsyncSession, client: AsyncClient) -> str:
    """Create tenant + user, return access_token."""
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(name="Profile Corp", slug="profile-corp")
    await repo.save(tenant)
    await db_session.commit()

    await client.post(
        "/api/v1/users/",
        json={
            "email": _EMAIL,
            "name": _NAME,
            "password": _PASSWORD,
            "tenant_id": str(tenant.id.value),
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": _EMAIL, "password": _PASSWORD},
    )
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_update_name(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    resp = await client.patch(
        "/api/v1/users/me",
        json={"full_name": "New Name"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["email"] == _EMAIL
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_update_avatar_url(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    url = "https://example.com/avatar.png"
    resp = await client.patch(
        "/api/v1/users/me",
        json={"avatar_url": url},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["avatar_url"] == url


@pytest.mark.asyncio
async def test_update_both_fields(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    resp = await client.patch(
        "/api/v1/users/me",
        json={"full_name": "Updated Name", "avatar_url": "https://example.com/pic.jpg"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Updated Name"
    assert data["avatar_url"] == "https://example.com/pic.jpg"


@pytest.mark.asyncio
async def test_empty_patch_is_noop(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    resp = await client.patch(
        "/api/v1/users/me",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == _NAME


@pytest.mark.asyncio
async def test_update_profile_requires_auth(client: AsyncClient):
    resp = await client.patch("/api/v1/users/me", json={"full_name": "Hacker"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_name_too_short_returns_422(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    resp = await client.patch(
        "/api/v1/users/me",
        json={"full_name": "X"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_me_returns_avatar_url(db_session: AsyncSession, client: AsyncClient):
    token = await _setup(db_session, client)
    url = "https://example.com/me.jpg"
    await client.patch(
        "/api/v1/users/me",
        json={"avatar_url": url},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["avatar_url"] == url
