"""Integration tests — Deliverable flow.

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


async def _create_project(
    client: AsyncClient, token: str, org_id: str, name: str = "My Project"
) -> str:
    resp = await client.post(
        "/api/v1/projects",
        json={"name": name, "description": "Test project", "org_id": org_id},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _submit_deliverable(
    client: AsyncClient, token: str, project_id: str, title: str = "Design v1"
) -> str:
    resp = await client.post(
        f"/api/v1/projects/{project_id}/deliverables",
        json={"title": title, "url_link": "https://figma.com/file/abc"},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_submit_deliverable_returns_201(
    db_session: AsyncSession, client: AsyncClient
):
    """Submitting a deliverable returns 201 with correct data."""
    tid = await _provision_tenant(db_session, "Corp A", "corp-a-del")
    token = await _register_and_login(client, tid, "owner@del-a.com")
    org_id = await _create_org(client, token, name="Del Corp A", slug="del-corp-a")
    project_id = await _create_project(client, token, org_id)

    resp = await client.post(
        f"/api/v1/projects/{project_id}/deliverables",
        json={"title": "Design v1", "url_link": "https://figma.com/file/abc"},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Design v1"
    assert data["url_link"] == "https://figma.com/file/abc"
    assert data["project_id"] == project_id
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_owner_can_approve_deliverable(
    db_session: AsyncSession, client: AsyncClient
):
    """OWNER approves a deliverable — 200 with status APPROVED."""
    tid = await _provision_tenant(db_session, "Corp B", "corp-b-del")
    token = await _register_and_login(client, tid, "owner@del-b.com")
    org_id = await _create_org(client, token, name="Del Corp B", slug="del-corp-b")
    project_id = await _create_project(client, token, org_id)
    deliverable_id = await _submit_deliverable(client, token, project_id)

    resp = await client.patch(
        f"/api/v1/deliverables/{deliverable_id}/approve",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "APPROVED"


@pytest.mark.asyncio
async def test_owner_can_request_changes(db_session: AsyncSession, client: AsyncClient):
    """OWNER requests changes — 200 with status CHANGES_REQUESTED."""
    tid = await _provision_tenant(db_session, "Corp C", "corp-c-del")
    token = await _register_and_login(client, tid, "owner@del-c.com")
    org_id = await _create_org(client, token, name="Del Corp C", slug="del-corp-c")
    project_id = await _create_project(client, token, org_id)
    deliverable_id = await _submit_deliverable(client, token, project_id)

    resp = await client.patch(
        f"/api/v1/deliverables/{deliverable_id}/request-changes",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "CHANGES_REQUESTED"


@pytest.mark.asyncio
async def test_member_cannot_approve_deliverable(
    db_session: AsyncSession, client: AsyncClient
):
    """MEMBER gets 403 when trying to approve a deliverable."""
    tid = await _provision_tenant(db_session, "Corp D", "corp-d-del")
    owner_token = await _register_and_login(
        client, tid, "owner@del-d.com", name="Owner"
    )
    member_token = await _register_and_login(
        client, tid, "member@del-d.com", name="Member"
    )
    org_id = await _create_org(
        client, owner_token, name="Del Corp D", slug="del-corp-d"
    )
    project_id = await _create_project(client, owner_token, org_id)
    deliverable_id = await _submit_deliverable(client, owner_token, project_id)

    # Invite member and accept
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "member@del-d.com", "role": "MEMBER"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    inv_id = resp.json()["id"]

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=_auth(member_token),
    )
    assert resp.status_code == 200, resp.text

    # Member tries to approve
    resp = await client.patch(
        f"/api/v1/deliverables/{deliverable_id}/approve",
        headers=_auth(member_token),
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_submit_deliverable_unknown_project_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    """Submitting a deliverable for a non-existent project returns 404."""
    tid = await _provision_tenant(db_session, "Corp E", "corp-e-del")
    token = await _register_and_login(client, tid, "owner@del-e.com")

    resp = await client.post(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000/deliverables",
        json={"title": "Ghost Deliverable", "url_link": "https://figma.com/file/xyz"},
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_unauthenticated_cannot_submit_deliverable(
    db_session: AsyncSession, client: AsyncClient
):
    """Request without JWT gets 401."""
    resp = await client.post(
        "/api/v1/projects/some-project-id/deliverables",
        json={"title": "Design v1", "url_link": "https://figma.com/file/abc"},
    )
    assert resp.status_code == 401, resp.text
