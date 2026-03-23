"""Integration tests — Registration error paths.

Tests Pydantic schema validation (422) and domain errors (409).
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import provision_tenant, register_user


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(
    db_session: AsyncSession, client: AsyncClient
):
    tid = await provision_tenant(db_session, "Dup Corp", "dup-corp")
    await register_user(client, tid, "dupe@test.com")

    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "dupe@test.com",
            "name": "Another",
            "password": "Password1!",
            "tenant_id": tid,
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "not-an-email",
            "name": "Test",
            "password": "Password1!",
            "tenant_id": "00000000-0000-4000-8000-000000000001",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_name_too_short_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "ok@test.com",
            "name": "A",
            "password": "Password1!",
            "tenant_id": "00000000-0000-4000-8000-000000000001",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_name_too_long_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "ok@test.com",
            "name": "A" * 101,
            "password": "Password1!",
            "tenant_id": "00000000-0000-4000-8000-000000000001",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_password_too_short_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "ok@test.com",
            "name": "Test",
            "password": "short",
            "tenant_id": "00000000-0000-4000-8000-000000000001",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_tenant_id_returns_422(client: AsyncClient):
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "ok@test.com",
            "name": "Test",
            "password": "Password1!",
            "tenant_id": "not-a-uuid",
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_fields_returns_422(client: AsyncClient):
    resp = await client.post("/api/v1/users/", json={})
    assert resp.status_code == 422
