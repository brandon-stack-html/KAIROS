"""Integration tests — Dashboard stats endpoint.

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
async def test_dashboard_stats_empty(db_session: AsyncSession, client: AsyncClient):
    """User with no orgs/projects gets zeroed-out stats."""
    tid = await _provision_tenant(db_session, "Stats Corp", "stats-corp")
    token = await _register_and_login(client, tid, "stats@example.com")

    resp = await client.get("/api/v1/dashboard/stats", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["organizations_count"] == 0
    assert data["projects_total"] == 0
    assert data["projects_active"] == 0
    assert data["projects_completed"] == 0
    assert data["deliverables_total"] == 0
    assert data["deliverables_pending"] == 0
    assert data["deliverables_approved"] == 0
    assert data["deliverables_changes_requested"] == 0
    assert data["invoices_total_amount"] == "0"
    assert data["invoices_paid_amount"] == "0"
    assert data["invoices_pending_amount"] == "0"


@pytest.mark.asyncio
async def test_dashboard_stats_with_org_and_project(
    db_session: AsyncSession, client: AsyncClient
):
    """User with an org and a project sees correct counts."""
    tid = await _provision_tenant(db_session, "Stats Corp 2", "stats-corp-2")
    token = await _register_and_login(client, tid, "owner@stats2.com")
    org_id = await _create_org(client, token, name="MyOrg", slug="myorg")

    # Create a project
    resp = await client.post(
        "/api/v1/projects",
        json={
            "name": "Dashboard Project",
            "description": "Test project for stats",
            "org_id": org_id,
        },
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text

    resp = await client.get("/api/v1/dashboard/stats", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["organizations_count"] >= 1
    assert data["projects_total"] >= 1
    assert data["projects_active"] >= 1


@pytest.mark.asyncio
async def test_dashboard_stats_requires_auth(
    db_session: AsyncSession, client: AsyncClient
):
    """Unauthenticated request returns 401."""
    await _provision_tenant(db_session, "Stats Corp 3", "stats-corp-3")

    resp = await client.get("/api/v1/dashboard/stats")
    assert resp.status_code == 401
