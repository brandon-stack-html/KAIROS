"""Integration tests — RemoveMember + ChangeMemberRole endpoints.

These endpoints previously had ZERO test coverage.
"""
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import (
    accept_invitation,
    auth_header,
    create_org,
    get_user_id_from_token,
    invite_member,
    provision_tenant,
    register_and_login,
)


async def _setup_org_with_member(
    db_session: AsyncSession, client: AsyncClient
) -> tuple[str, str, str, str, str, str]:
    """Provision tenant + 2 users + org + invite + accept.

    Returns (tenant_id, org_id, owner_token, member_token, owner_id, member_id).
    """
    tid = await provision_tenant(db_session, f"Corp-{uuid.uuid4().hex[:6]}", f"corp-{uuid.uuid4().hex[:6]}")
    owner_token = await register_and_login(client, tid, f"owner-{uuid.uuid4().hex[:6]}@test.com", name="Owner")
    member_token = await register_and_login(client, tid, f"member-{uuid.uuid4().hex[:6]}@test.com", name="Member")

    owner_id = get_user_id_from_token(owner_token)
    member_id = get_user_id_from_token(member_token)

    org = await create_org(client, owner_token, "Test Org", f"test-org-{uuid.uuid4().hex[:6]}")
    inv = await invite_member(client, owner_token, org["id"], f"member-{uuid.uuid4().hex[:6]}@test.com")

    # We need the member's actual email for the invitation, let me fix this approach
    # Actually, invite_member uses the email to create invitation, and accept uses the member's JWT
    # The member's email was registered above — let me restructure

    return tid, org["id"], owner_token, member_token, owner_id, member_id


# The helper above has an issue: the invitation email must match the registered member's email.
# Let me use a cleaner approach with fixed emails per test.


async def _setup(
    db_session: AsyncSession,
    client: AsyncClient,
    suffix: str,
) -> tuple[str, str, str, str, str, str]:
    """Setup tenant + owner + member + org with member joined.

    Returns (tenant_id, org_id, owner_token, member_token, owner_id, member_id).
    """
    tid = await provision_tenant(db_session, f"Corp {suffix}", f"corp-{suffix}")
    owner_email = f"owner-{suffix}@test.com"
    member_email = f"member-{suffix}@test.com"

    owner_token = await register_and_login(client, tid, owner_email, name="Owner")
    member_token = await register_and_login(client, tid, member_email, name="Member")

    owner_id = get_user_id_from_token(owner_token)
    member_id = get_user_id_from_token(member_token)

    org = await create_org(client, owner_token, f"Org {suffix}", f"org-{suffix}")
    inv = await invite_member(client, owner_token, org["id"], member_email)
    await accept_invitation(client, member_token, org["id"], inv["id"])

    return tid, org["id"], owner_token, member_token, owner_id, member_id


# ── RemoveMember ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_remove_member_happy_path(db_session: AsyncSession, client: AsyncClient):
    _, org_id, owner_token, _, _, member_id = await _setup(db_session, client, "rm-ok")

    resp = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{member_id}",
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_nonexistent_member_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, owner_token, _, _, _ = await _setup(db_session, client, "rm-404")

    fake_user_id = str(uuid.uuid4())
    resp = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{fake_user_id}",
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_remove_last_owner_returns_400(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, owner_token, _, owner_id, _ = await _setup(db_session, client, "rm-owner")

    resp = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{owner_id}",
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_member_cannot_remove_returns_403(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, _, member_token, owner_id, _ = await _setup(db_session, client, "rm-403")

    # Member tries to remove the owner — should fail with 403
    resp = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{owner_id}",
        headers=auth_header(member_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_remove_from_nonexistent_org_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    tid = await provision_tenant(db_session, "Rm Ghost Corp", "rm-ghost-corp")
    token = await register_and_login(client, tid, "user@rmghost.com", name="User")

    fake_org_id = str(uuid.uuid4())
    fake_user_id = str(uuid.uuid4())
    resp = await client.delete(
        f"/api/v1/organizations/{fake_org_id}/members/{fake_user_id}",
        headers=auth_header(token),
    )
    assert resp.status_code == 404


# ── ChangeMemberRole ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_change_role_happy_path(db_session: AsyncSession, client: AsyncClient):
    _, org_id, owner_token, _, _, member_id = await _setup(db_session, client, "role-ok")

    resp = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{member_id}/role",
        json={"role": "ADMIN"},
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_demote_last_owner_returns_400(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, owner_token, _, owner_id, _ = await _setup(db_session, client, "role-demote")

    resp = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{owner_id}/role",
        json={"role": "MEMBER"},
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_member_cannot_change_role_returns_403(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, _, member_token, owner_id, _ = await _setup(db_session, client, "role-403")

    resp = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{owner_id}/role",
        json={"role": "MEMBER"},
        headers=auth_header(member_token),
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_change_role_nonexistent_member_returns_404(
    db_session: AsyncSession, client: AsyncClient
):
    _, org_id, owner_token, _, _, _ = await _setup(db_session, client, "role-404")

    fake_user_id = str(uuid.uuid4())
    resp = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{fake_user_id}/role",
        json={"role": "ADMIN"},
        headers=auth_header(owner_token),
    )
    assert resp.status_code == 404
