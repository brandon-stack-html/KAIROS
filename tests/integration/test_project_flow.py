"""Integration tests — Project flow.

Tests run against SQLite in-memory via the test client fixture.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


async def _provision_tenant(db_session: AsyncSession, name: str, slug: str) -> str:
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(name=name, slug=slug)
    await repo.save(tenant)
    await db_session.commit()
    return tenant.id.value


async def _register_and_login(
    client: AsyncClient,
    tenant_id: str,
    email: str,
    password: str = "Password1!",
    name: str = "Test User",
) -> str:
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": email,
            "name": name,
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


async def _create_org(
    client: AsyncClient, token: str, name: str = "Acme", slug: str = "acme"
) -> str:
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": name, "slug": slug},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_owner_can_create_project(db_session: AsyncSession, client: AsyncClient):
    """OWNER creates a project — 201 with correct data."""
    tid = await _provision_tenant(db_session, "Corp A", "corp-a")
    token = await _register_and_login(client, tid, "owner@a.com")
    org_id = await _create_org(client, token)

    resp = await client.post(
        "/api/v1/projects",
        json={
            "name": "Website Redesign",
            "description": "Redesign the website",
            "org_id": org_id,
        },
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["name"] == "Website Redesign"
    assert data["description"] == "Redesign the website"
    assert data["org_id"] == org_id
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_member_cannot_create_project(
    db_session: AsyncSession, client: AsyncClient
):
    """MEMBER gets 403 when trying to create a project."""
    tid = await _provision_tenant(db_session, "Corp B", "corp-b")
    owner_token = await _register_and_login(client, tid, "owner@b.com", name="Owner")
    member_token = await _register_and_login(client, tid, "member@b.com", name="Member")
    org_id = await _create_org(client, owner_token, name="Beta Corp", slug="beta-corp")

    # Invite and accept as MEMBER
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "member@b.com", "role": "MEMBER"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    inv_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=_auth(member_token),
    )
    assert resp.status_code == 200, resp.text

    # Member tries to create project
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "My Project", "description": "", "org_id": org_id},
        headers=_auth(member_token),
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_list_projects_returns_user_projects(
    db_session: AsyncSession, client: AsyncClient
):
    """Listing projects returns all projects the user's orgs have."""
    tid = await _provision_tenant(db_session, "Corp C", "corp-c")
    token = await _register_and_login(client, tid, "owner@c.com")
    org_id = await _create_org(client, token, name="Gamma Corp", slug="gamma-corp")

    # Create 2 projects
    for i in range(2):
        resp = await client.post(
            "/api/v1/projects",
            json={"name": f"Project {i}", "description": "", "org_id": org_id},
            headers=_auth(token),
        )
        assert resp.status_code == 201, resp.text

    resp = await client.get("/api/v1/projects", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_tenant_isolation(db_session: AsyncSession, client: AsyncClient):
    """Projects of tenant A are invisible for a user in tenant B."""
    tid_a = await _provision_tenant(db_session, "Tenant A", "tenant-a")
    tid_b = await _provision_tenant(db_session, "Tenant B", "tenant-b")

    token_a = await _register_and_login(client, tid_a, "owner@ta.com")
    org_id_a = await _create_org(client, token_a, name="Org A", slug="org-a")
    await client.post(
        "/api/v1/projects",
        json={"name": "Secret Project", "description": "", "org_id": org_id_a},
        headers=_auth(token_a),
    )

    token_b = await _register_and_login(client, tid_b, "owner@tb.com")
    resp = await client.get("/api/v1/projects", headers=_auth(token_b))
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_project_unknown_org_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    """Creating a project for a non-existent org returns 404."""
    tid = await _provision_tenant(db_session, "Corp D", "corp-d")
    token = await _register_and_login(client, tid, "owner@d.com")

    resp = await client.post(
        "/api/v1/projects",
        json={
            "name": "Ghost Project",
            "description": "",
            "org_id": "00000000-0000-0000-0000-000000000000",
        },
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_unauthenticated_cannot_create_project(
    db_session: AsyncSession, client: AsyncClient
):
    """Request without JWT gets 401."""
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "Project X", "description": "", "org_id": "some-id"},
    )
    assert resp.status_code == 401, resp.text
