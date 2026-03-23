"""Integration tests — Invoice flow.

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


async def _issue_invoice(
    client: AsyncClient,
    token: str,
    org_id: str,
    title: str = "Invoice #1",
    amount: str = "500.00",
) -> str:
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invoices",
        json={"title": title, "amount": amount},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_owner_can_issue_invoice(db_session: AsyncSession, client: AsyncClient):
    """OWNER issues an invoice — 201, amount returned as string."""
    tid = await _provision_tenant(db_session, "Corp A", "corp-a-inv")
    token = await _register_and_login(client, tid, "owner@inv-a.com")
    org_id = await _create_org(client, token, name="Inv Corp A", slug="inv-corp-a")

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invoices",
        json={"title": "Website Project", "amount": "1500.50"},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["title"] == "Website Project"
    assert data["amount"] == "1500.50"
    assert data["status"] == "DRAFT"
    assert data["paid_at"] is None
    assert isinstance(data["amount"], str)


@pytest.mark.asyncio
async def test_owner_can_mark_invoice_paid(
    db_session: AsyncSession, client: AsyncClient
):
    """OWNER marks an invoice as paid — 200, status PAID."""
    tid = await _provision_tenant(db_session, "Corp B", "corp-b-inv")
    token = await _register_and_login(client, tid, "owner@inv-b.com")
    org_id = await _create_org(client, token, name="Inv Corp B", slug="inv-corp-b")
    invoice_id = await _issue_invoice(client, token, org_id)

    resp = await client.patch(
        f"/api/v1/invoices/{invoice_id}/paid",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "PAID"
    assert data["paid_at"] is not None


@pytest.mark.asyncio
async def test_double_mark_paid_returns_400(
    db_session: AsyncSession, client: AsyncClient
):
    """Marking an already-paid invoice returns 400 (InvoiceAlreadyPaidError)."""
    tid = await _provision_tenant(db_session, "Corp C", "corp-c-inv")
    token = await _register_and_login(client, tid, "owner@inv-c.com")
    org_id = await _create_org(client, token, name="Inv Corp C", slug="inv-corp-c")
    invoice_id = await _issue_invoice(client, token, org_id)

    resp = await client.patch(
        f"/api/v1/invoices/{invoice_id}/paid", headers=_auth(token)
    )
    assert resp.status_code == 200, resp.text

    resp = await client.patch(
        f"/api/v1/invoices/{invoice_id}/paid", headers=_auth(token)
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.asyncio
async def test_member_cannot_issue_invoice(
    db_session: AsyncSession, client: AsyncClient
):
    """MEMBER gets 403 when trying to issue an invoice."""
    tid = await _provision_tenant(db_session, "Corp D", "corp-d-inv")
    owner_token = await _register_and_login(
        client, tid, "owner@inv-d.com", name="Owner"
    )
    member_token = await _register_and_login(
        client, tid, "member@inv-d.com", name="Member"
    )
    org_id = await _create_org(
        client, owner_token, name="Inv Corp D", slug="inv-corp-d"
    )

    # Invite + accept as MEMBER
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "member@inv-d.com", "role": "MEMBER"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    inv_id = resp.json()["id"]
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=_auth(member_token),
    )
    assert resp.status_code == 200, resp.text

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invoices",
        json={"title": "Unauthorized Invoice", "amount": "100.00"},
        headers=_auth(member_token),
    )
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_issue_invoice_unknown_org_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    """Issuing an invoice for a non-existent org returns 404."""
    tid = await _provision_tenant(db_session, "Corp E", "corp-e-inv")
    token = await _register_and_login(client, tid, "owner@inv-e.com")

    resp = await client.post(
        "/api/v1/organizations/00000000-0000-0000-0000-000000000000/invoices",
        json={"title": "Ghost Invoice", "amount": "200.00"},
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_unauthenticated_cannot_issue_invoice(
    db_session: AsyncSession, client: AsyncClient
):
    """Request without JWT gets 401."""
    resp = await client.post(
        "/api/v1/organizations/some-org-id/invoices",
        json={"title": "Anon Invoice", "amount": "100.00"},
    )
    assert resp.status_code == 401, resp.text
