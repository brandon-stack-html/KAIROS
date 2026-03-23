"""Integration tests — API gap endpoints for frontend connectivity.

Covers: tenant lookup/create, GET /users/me, GET org/project detail,
list deliverables, list invoices.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


async def _provision_tenant(db_session: AsyncSession, slug: str) -> str:
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(name="Test Tenant", slug=slug)
    await repo.save(tenant)
    await db_session.commit()
    return tenant.id.value


async def _register_and_login(
    client: AsyncClient,
    tenant_id: str,
    email: str,
    password: str = "Password1!",
) -> str:
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "name": "Test User",
            "password": password,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 201, resp.text
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client: AsyncClient, token: str, name: str, slug: str) -> str:
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": name, "slug": slug},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _create_project(
    client: AsyncClient, token: str, org_id: str, name: str
) -> str:
    resp = await client.post(
        "/api/v1/projects",
        json={"name": name, "description": "Test project", "org_id": org_id},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tenant endpoints ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_tenant_by_slug_200(db_session: AsyncSession, client: AsyncClient):
    """GET /tenants/by-slug/{slug} with existing tenant → 200."""
    slug = f"test-{uuid.uuid4().hex[:8]}"
    await _provision_tenant(db_session, slug)

    resp = await client.get(f"/api/v1/tenants/by-slug/{slug}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["slug"] == slug
    assert "id" in data
    assert "name" in data


@pytest.mark.asyncio
async def test_get_tenant_by_slug_404(client: AsyncClient):
    """GET /tenants/by-slug/{slug} with unknown slug → 404."""
    resp = await client.get("/api/v1/tenants/by-slug/no-existe-slug")
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_create_tenant_201(client: AsyncClient):
    """POST /tenants → 201 with new tenant."""
    slug = f"new-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/tenants",
        json={"name": "New Tenant", "slug": slug},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["slug"] == slug
    assert data["name"] == "New Tenant"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_tenant_duplicate_slug_409(client: AsyncClient):
    """POST /tenants with duplicate slug → 409."""
    slug = f"dup-{uuid.uuid4().hex[:8]}"
    resp = await client.post(
        "/api/v1/tenants",
        json={"name": "First", "slug": slug},
    )
    assert resp.status_code == 201, resp.text

    resp = await client.post(
        "/api/v1/tenants",
        json={"name": "Second", "slug": slug},
    )
    assert resp.status_code == 409, resp.text


# ── GET /users/me ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_me_200(db_session: AsyncSession, client: AsyncClient):
    """GET /users/me with valid JWT → 200 with user details."""
    tid = await _provision_tenant(db_session, f"me-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "me@test.com")

    resp = await client.get("/api/v1/users/me", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["email"] == "me@test.com"
    assert data["name"] == "Test User"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_401(client: AsyncClient):
    """GET /users/me without JWT → 401."""
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401, resp.text


# ── GET /organizations/{id} ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_organization_200(db_session: AsyncSession, client: AsyncClient):
    """GET /organizations/{id} → 200 with members."""
    tid = await _provision_tenant(db_session, f"org-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "orgdetail@test.com")
    org_id = await _create_org(
        client, token, "Detail Org", f"detail-{uuid.uuid4().hex[:8]}"
    )

    resp = await client.get(f"/api/v1/organizations/{org_id}", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == org_id
    assert data["name"] == "Detail Org"
    assert len(data["members"]) >= 1


@pytest.mark.asyncio
async def test_get_organization_404(db_session: AsyncSession, client: AsyncClient):
    """GET /organizations/{id} with unknown id → 404."""
    tid = await _provision_tenant(db_session, f"org404-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "org404@test.com")

    resp = await client.get(
        "/api/v1/organizations/00000000-0000-0000-0000-000000000000",
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


# ── GET /projects/{id} ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_project_200(db_session: AsyncSession, client: AsyncClient):
    """GET /projects/{id} → 200."""
    tid = await _provision_tenant(db_session, f"proj-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "projdetail@test.com")
    org_id = await _create_org(
        client, token, "Proj Org", f"projorg-{uuid.uuid4().hex[:8]}"
    )
    project_id = await _create_project(client, token, org_id, "Detail Project")

    resp = await client.get(f"/api/v1/projects/{project_id}", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["id"] == project_id
    assert data["name"] == "Detail Project"


@pytest.mark.asyncio
async def test_get_project_404(db_session: AsyncSession, client: AsyncClient):
    """GET /projects/{id} with unknown id → 404."""
    tid = await _provision_tenant(db_session, f"proj404-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "proj404@test.com")

    resp = await client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000",
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


# ── GET /projects/{id}/deliverables ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_deliverables_200(db_session: AsyncSession, client: AsyncClient):
    """GET /projects/{id}/deliverables → 200 list."""
    tid = await _provision_tenant(db_session, f"deliv-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "deliv@test.com")
    org_id = await _create_org(
        client, token, "Deliv Org", f"delivorg-{uuid.uuid4().hex[:8]}"
    )
    project_id = await _create_project(client, token, org_id, "Deliv Project")

    # Submit a deliverable
    await client.post(
        f"/api/v1/projects/{project_id}/deliverables",
        json={"title": "Mockup v1", "url_link": "https://figma.com/abc"},
        headers=_auth(token),
    )

    resp = await client.get(
        f"/api/v1/projects/{project_id}/deliverables",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Mockup v1"


# ── GET /organizations/{id}/invoices ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_invoices_200(db_session: AsyncSession, client: AsyncClient):
    """GET /organizations/{id}/invoices → 200 list."""
    tid = await _provision_tenant(db_session, f"inv-{uuid.uuid4().hex[:8]}")
    token = await _register_and_login(client, tid, "inv@test.com")
    org_id = await _create_org(
        client, token, "Inv Org", f"invorg-{uuid.uuid4().hex[:8]}"
    )

    # Issue an invoice
    await client.post(
        f"/api/v1/organizations/{org_id}/invoices",
        json={"title": "Invoice #1", "amount": "500.00"},
        headers=_auth(token),
    )

    resp = await client.get(
        f"/api/v1/organizations/{org_id}/invoices",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Invoice #1"
    assert data[0]["amount"] == "500.00"
