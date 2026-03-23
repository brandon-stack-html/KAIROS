"""Integration tests — AI Summary endpoint.

Uses InMemoryAiService (injected via conftest override).
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


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_summary_with_deliverables_returns_200(
    db_session: AsyncSession, client: AsyncClient
):
    """GET summary with project + deliverables → 200, {"summary": str}."""
    tid = await _provision_tenant(db_session, "Corp A", "corp-a-ai")
    token = await _register_and_login(client, tid, "owner@ai-a.com")
    org_id = await _create_org(client, token, "AI Corp A", "ai-corp-a")
    project_id = await _create_project(client, token, org_id, "Website Redesign")

    # Submit a deliverable
    resp = await client.post(
        f"/api/v1/projects/{project_id}/deliverables",
        json={"title": "Homepage mockup", "url_link": "https://figma.com/abc"},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text

    resp = await client.get(
        f"/api/v1/projects/{project_id}/summary", headers=_auth(token)
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "summary" in data
    assert isinstance(data["summary"], str)
    assert "Website Redesign" in data["summary"]
    assert "1" in data["summary"]  # InMemoryAiService includes deliverable count


@pytest.mark.asyncio
async def test_summary_without_deliverables_returns_200(
    db_session: AsyncSession, client: AsyncClient
):
    """GET summary for a project with no deliverables → 200, mentions 0 entregables."""
    tid = await _provision_tenant(db_session, "Corp B", "corp-b-ai")
    token = await _register_and_login(client, tid, "owner@ai-b.com")
    org_id = await _create_org(client, token, "AI Corp B", "ai-corp-b")
    project_id = await _create_project(client, token, org_id, "Mobile App")

    resp = await client.get(
        f"/api/v1/projects/{project_id}/summary", headers=_auth(token)
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "summary" in data
    assert "0" in data["summary"]


@pytest.mark.asyncio
async def test_summary_unknown_project_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    """GET summary for non-existent project → 404."""
    tid = await _provision_tenant(db_session, "Corp C", "corp-c-ai")
    token = await _register_and_login(client, tid, "owner@ai-c.com")

    resp = await client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000/summary",
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_summary_unauthenticated_returns_401(
    db_session: AsyncSession, client: AsyncClient
):
    """GET summary without JWT → 401."""
    resp = await client.get("/api/v1/projects/some-project-id/summary")
    assert resp.status_code == 401, resp.text
