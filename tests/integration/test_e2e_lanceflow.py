"""E2E test — full LanceFlow MVP journey (16 steps).

Covers the complete freelancer workflow from registration to logout:
register → login → refresh → org → invite → accept →
project → deliverable → approve → invoice → paid → ai summary → logout

Uses SQLite in-memory via the test client fixture.
InMemoryAiService is injected via the conftest override.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)


async def _provision_tenant(db_session: AsyncSession) -> str:
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(
        name="LanceFlow Tenant", slug=f"lanceflow-{uuid.uuid4().hex[:8]}"
    )
    await repo.save(tenant)
    await db_session.commit()
    return tenant.id.value


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_full_lanceflow_journey(
    db_session: AsyncSession,
    client: AsyncClient,
    email_sender,
):
    """Complete LanceFlow MVP workflow — 16 steps, all green."""
    tenant_id = await _provision_tenant(db_session)
    owner_password = "StrongPass1!"

    # ── 1. REGISTRO ──────────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "owner@lanceflow.com",
            "name": "LanceFlow Owner",
            "password": owner_password,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 201, resp.text

    # ── 2. LOGIN ─────────────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "owner@lanceflow.com", "password": owner_password},
    )
    assert resp.status_code == 200, resp.text
    login_data = resp.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data
    access_token = login_data["access_token"]
    refresh_token = login_data["refresh_token"]

    # ── 3. REFRESH TOKEN ─────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200, resp.text
    refresh_data = resp.json()
    access_token = refresh_data["access_token"]
    refresh_token = refresh_data["refresh_token"]

    # ── 4. CREAR ORGANIZACIÓN ─────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": "LanceFlow Studio", "slug": "lanceflow-studio"},
        headers=_auth(access_token),
    )
    assert resp.status_code == 201, resp.text
    org_data = resp.json()
    org_id = org_data["id"]
    assert org_data["name"] == "LanceFlow Studio"
    members = org_data.get("members", [])
    owner_member = next((m for m in members if m["role"] == "OWNER"), None)
    assert owner_member is not None, "Owner must appear as OWNER in members"

    # ── 5. INVITAR MIEMBRO ────────────────────────────────────────────────────
    email_sender.clear()
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "client@empresa.com", "role": "MEMBER"},
        headers=_auth(access_token),
    )
    assert resp.status_code == 201, resp.text
    inv_data = resp.json()
    invitation_id = inv_data["id"]
    assert len(email_sender.sent) == 1, "Invitation email must be sent"

    # ── 6. REGISTRAR SEGUNDO USUARIO (el cliente) ────────────────────────────
    client_password = "ClientPass1!"
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "client@empresa.com",
            "name": "Client User",
            "password": client_password,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 201, resp.text

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "client@empresa.com", "password": client_password},
    )
    assert resp.status_code == 200, resp.text
    client_access_token = resp.json()["access_token"]

    # ── 7. ACEPTAR INVITACIÓN ─────────────────────────────────────────────────
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{invitation_id}/accept",
        headers=_auth(client_access_token),
    )
    assert resp.status_code == 200, resp.text

    # ── 8. CREAR PROYECTO ─────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/projects",
        json={
            "name": "Website Rediseño",
            "description": "Rediseño completo del sitio corporativo",
            "org_id": org_id,
        },
        headers=_auth(access_token),
    )
    assert resp.status_code == 201, resp.text
    project_data = resp.json()
    project_id = project_data["id"]
    assert project_data["status"] == "ACTIVE"
    assert project_data["name"] == "Website Rediseño"

    # ── 9. LISTAR PROYECTOS ───────────────────────────────────────────────────
    resp = await client.get(
        f"/api/v1/projects?org_id={org_id}",
        headers=_auth(access_token),
    )
    assert resp.status_code == 200, resp.text
    projects = resp.json()
    assert any(p["id"] == project_id for p in projects), "Project must appear in list"

    # ── 10. SUBMIT DELIVERABLE ────────────────────────────────────────────────
    resp = await client.post(
        f"/api/v1/projects/{project_id}/deliverables",
        json={"title": "Homepage v1", "url_link": "https://figma.com/file/homepage-v1"},
        headers=_auth(access_token),
    )
    assert resp.status_code == 201, resp.text
    deliverable_data = resp.json()
    deliverable_id = deliverable_data["id"]
    assert deliverable_data["status"] == "PENDING"
    assert deliverable_data["title"] == "Homepage v1"

    # ── 11. APROBAR DELIVERABLE ───────────────────────────────────────────────
    resp = await client.patch(
        f"/api/v1/deliverables/{deliverable_id}/approve",
        headers=_auth(access_token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "APPROVED"

    # ── 12. CREAR INVOICE ─────────────────────────────────────────────────────
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invoices",
        json={"title": "Factura #001", "amount": "1500.00"},
        headers=_auth(access_token),
    )
    assert resp.status_code == 201, resp.text
    invoice_data = resp.json()
    invoice_id = invoice_data["id"]
    assert invoice_data["status"] == "DRAFT"
    assert invoice_data["amount"] == "1500.00"
    assert invoice_data["paid_at"] is None

    # ── 13. MARCAR INVOICE COMO PAGADA ────────────────────────────────────────
    resp = await client.patch(
        f"/api/v1/invoices/{invoice_id}/paid",
        headers=_auth(access_token),
    )
    assert resp.status_code == 200, resp.text
    paid_data = resp.json()
    assert paid_data["status"] == "PAID"
    assert paid_data["paid_at"] is not None

    # ── 14. GENERAR AI SUMMARY ────────────────────────────────────────────────
    resp = await client.get(
        f"/api/v1/projects/{project_id}/summary",
        headers=_auth(access_token),
    )
    assert resp.status_code == 200, resp.text
    summary_data = resp.json()
    assert "summary" in summary_data
    assert isinstance(summary_data["summary"], str)
    assert len(summary_data["summary"]) > 0

    # ── 15. LOGOUT ────────────────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers=_auth(access_token),
    )
    assert resp.status_code == 204, resp.text

    # ── 16. VERIFICAR QUE REFRESH YA NO FUNCIONA ─────────────────────────────
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 401, resp.text
