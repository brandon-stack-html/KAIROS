"""Integration tests — InviteMember sends an email via InMemoryEmailSender."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.in_memory.email_sender import InMemoryEmailSender
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
    """Register a user and return their access token."""
    resp = await client.post(
        "/api/v1/users/",
        json={"email": email, "name": name, "password": password, "tenant_id": tenant_id},
    )
    assert resp.status_code == 201, resp.text

    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


async def _create_org(client: AsyncClient, token: str, name: str, slug: str) -> str:
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": name, "slug": slug},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invite_member_sends_email_to_invitee(
    client: AsyncClient,
    db_session: AsyncSession,
    email_sender: InMemoryEmailSender,
):
    """After inviting a member, the invitee receives an invitation email."""
    tenant_id = await _provision_tenant(db_session, "Test Tenant", "test-tenant")
    token = await _register_and_login(client, tenant_id, "owner@example.com", name="Owner")
    org_id = await _create_org(client, token, "ACME Corp", "acme-corp")

    email_sender.clear()  # ignore registration welcome emails

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "newmember@example.com", "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text

    emails = email_sender.find_by_to("newmember@example.com")
    assert len(emails) == 1


@pytest.mark.asyncio
async def test_invitation_email_contains_accept_url(
    client: AsyncClient,
    db_session: AsyncSession,
    email_sender: InMemoryEmailSender,
):
    """Invitation email body must contain the invitation accept URL."""
    tenant_id = await _provision_tenant(db_session, "Tenant B", "tenant-b")
    token = await _register_and_login(client, tenant_id, "owner2@example.com", name="Owner2")
    org_id = await _create_org(client, token, "Beta Corp", "beta-corp")
    email_sender.clear()

    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "invited@example.com", "role": "ADMIN"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    invitation_id = resp.json()["id"]

    emails = email_sender.find_by_to("invited@example.com")
    assert len(emails) == 1
    msg = emails[0]
    assert invitation_id in msg.text_body or invitation_id in msg.html_body


@pytest.mark.asyncio
async def test_invitation_email_contains_org_name(
    client: AsyncClient,
    db_session: AsyncSession,
    email_sender: InMemoryEmailSender,
):
    """Invitation email must mention the organization name."""
    tenant_id = await _provision_tenant(db_session, "Tenant C", "tenant-c")
    token = await _register_and_login(client, tenant_id, "owner3@example.com", name="Owner3")
    org_id = await _create_org(client, token, "Gamma Inc", "gamma-inc")
    email_sender.clear()

    await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "gamma_invite@example.com", "role": "MEMBER"},
        headers={"Authorization": f"Bearer {token}"},
    )

    emails = email_sender.find_by_to("gamma_invite@example.com")
    assert len(emails) == 1
    msg = emails[0]
    assert "Gamma Inc" in msg.text_body or "Gamma Inc" in msg.html_body


@pytest.mark.asyncio
async def test_register_user_sends_welcome_email(
    client: AsyncClient,
    db_session: AsyncSession,
    email_sender: InMemoryEmailSender,
):
    """Registering a user triggers a welcome email."""
    tenant_id = await _provision_tenant(db_session, "Tenant W", "tenant-w")
    email_sender.clear()

    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "welcome@example.com",
            "name": "Welcome User",
            "password": "Password1!",
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 201, resp.text

    emails = email_sender.find_by_to("welcome@example.com")
    assert len(emails) == 1
    assert "Welcome User" in emails[0].text_body
