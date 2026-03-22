"""Integration tests — Organization flow (create → invite → accept → verify).

Tests run against SQLite in-memory via the test client fixture.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.shared.tenant_id import TenantId
from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


async def _provision_tenant(db_session: AsyncSession, name: str, slug: str) -> str:
    """Create a tenant and return its id string."""
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


# ── Test 1: Full create → invite → accept flow ────────────────────────────────


@pytest.mark.asyncio
async def test_create_invite_accept_membership(
    db_session: AsyncSession, client: AsyncClient
):
    """Happy path: owner creates org, invites member, member accepts."""
    tid = await _provision_tenant(db_session, "Org Corp", "org-corp")

    owner_token = await _register_and_login(
        client, tid, "owner@org.com", name="Owner"
    )
    member_token = await _register_and_login(
        client, tid, "member@org.com", name="Member"
    )

    # 1. Create org
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": "Acme Corp", "slug": "acme-corp"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    org = resp.json()
    org_id = org["id"]
    assert len(org["members"]) == 1
    assert org["members"][0]["role"] == "OWNER"

    # 2. Invite member
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "member@org.com", "role": "MEMBER"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    inv = resp.json()
    inv_id = inv["id"]
    assert inv["role"] == "MEMBER"

    # 3. Member accepts invitation
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=_auth(member_token),
    )
    assert resp.status_code == 200, resp.text
    updated_org = resp.json()
    assert len(updated_org["members"]) == 2
    roles = {m["role"] for m in updated_org["members"]}
    assert roles == {"OWNER", "MEMBER"}


# ── Test 2: Tenant isolation — other tenant cannot see org ────────────────────


@pytest.mark.asyncio
async def test_tenant_isolation_list_organizations(
    db_session: AsyncSession, client: AsyncClient
):
    """User from tenant B cannot see organizations from tenant A."""
    tid_a = await _provision_tenant(db_session, "Tenant A", "tenant-a")
    tid_b = await _provision_tenant(db_session, "Tenant B", "tenant-b")

    token_a = await _register_and_login(client, tid_a, "user-a@example.com", name="User A")
    token_b = await _register_and_login(client, tid_b, "user-b@example.com", name="User B")

    # Tenant A creates an org
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": "Private Org", "slug": "private-org"},
        headers=_auth(token_a),
    )
    assert resp.status_code == 201, resp.text

    # Tenant B lists their orgs — should be empty
    resp = await client.get(
        "/api/v1/organizations",
        headers=_auth(token_b),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


# ── Test 3: MEMBER cannot invite ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_member_cannot_invite(db_session: AsyncSession, client: AsyncClient):
    """A MEMBER role should receive 403 when trying to invite someone."""
    tid = await _provision_tenant(db_session, "Invite Corp", "invite-corp")

    owner_token = await _register_and_login(client, tid, "owner2@invite.com", name="Owner2")
    member_token = await _register_and_login(client, tid, "member2@invite.com", name="Member2")
    outsider_email = "outsider@invite.com"
    await _register_and_login(client, tid, outsider_email, name="Outsider")

    # Create org
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": "Invite Corp", "slug": "invite-corp-org"},
        headers=_auth(owner_token),
    )
    org_id = resp.json()["id"]

    # Invite member2
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "member2@invite.com", "role": "MEMBER"},
        headers=_auth(owner_token),
    )
    inv_id = resp.json()["id"]

    # member2 accepts
    await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=_auth(member_token),
    )

    # member2 tries to invite outsider → should get 403
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": outsider_email, "role": "MEMBER"},
        headers=_auth(member_token),
    )
    assert resp.status_code == 403, resp.text


# ── Test 4: Expired invitation returns 400 ───────────────────────────────────


@pytest.mark.asyncio
async def test_accept_expired_invitation_returns_400(
    db_session: AsyncSession, client: AsyncClient
):
    """Accepting an expired invitation should return 400."""
    from datetime import timedelta

    from src.domain.organization.invitation import Invitation
    from src.domain.organization.organization import Organization
    from src.domain.shared.role import Role
    from src.domain.shared.tenant_id import TenantId
    from src.domain.user.user import UserEmail, UserId
    from src.infrastructure.persistence.sqlalchemy.invitation_repository import (
        SqlAlchemyInvitationRepository,
    )
    from src.infrastructure.persistence.sqlalchemy.organization_repository import (
        SqlAlchemyOrganizationRepository,
    )
    from src.domain.shared.invitation_id import InvitationId
    from datetime import UTC, datetime

    tid_str = await _provision_tenant(db_session, "Expire Corp", "expire-corp")
    tid = TenantId.from_str(tid_str)

    owner_token = await _register_and_login(client, tid_str, "owner3@exp.com", name="Owner3")
    member_token = await _register_and_login(client, tid_str, "member3@exp.com", name="Member3")

    # Create org directly via domain + repository (bypass UoW for setup)
    owner_id_str = None
    import jwt as pyjwt
    from src.infrastructure.security.jwt_handler import decode_token
    owner_payload = decode_token(owner_token)
    owner_id_str = owner_payload["sub"]

    org = Organization.create(
        name="Expire Corp",
        slug="expire-corp-org",
        owner_id=UserId(owner_id_str),
        tenant_id=tid,
    )
    org_repo = SqlAlchemyOrganizationRepository(db_session, tenant_id=tid_str)
    await org_repo.save(org)
    await db_session.commit()

    # Create an already-expired invitation directly
    expired_inv = Invitation(
        id=InvitationId.generate(),
        org_id=org.id.value,
        invitee_email=UserEmail("member3@exp.com"),
        inviter_id=UserId(owner_id_str),
        role=Role.MEMBER,
        expires_at=datetime.now(UTC) - timedelta(days=1),
    )
    inv_repo = SqlAlchemyInvitationRepository(db_session)
    await inv_repo.save(expired_inv)
    await db_session.commit()

    # member3 tries to accept the expired invitation
    resp = await client.post(
        f"/api/v1/organizations/{org.id.value}/invitations/{expired_inv.id.value}/accept",
        headers=_auth(member_token),
    )
    assert resp.status_code == 400, resp.text
