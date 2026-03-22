"""E2E smoke test — full user journey through all major endpoints.

One sequential test that exercises the complete workflow:
  register → login → create org → invite → accept → list → change role → remove → refresh → logout

Uses the same conftest.py fixtures (SQLite in-memory, handler overrides).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import auth_header, get_user_id_from_token, provision_tenant


@pytest.mark.asyncio
async def test_full_user_journey(
    db_session: AsyncSession, client: AsyncClient, email_sender
):
    """End-to-end: exercises every major endpoint in a realistic order."""

    # ── Step 1: Provision tenant ─────────────────────────────────────────
    tid = await provision_tenant(db_session, "E2E Corp", "e2e-corp")

    # ── Step 2: Register User A ──────────────────────────────────────────
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "alice@e2e.com",
            "name": "Alice",
            "password": "AlicePass1!",
            "tenant_id": tid,
        },
    )
    assert resp.status_code == 201, resp.text
    user_a = resp.json()
    assert user_a["email"] == "alice@e2e.com"

    # ── Step 3: Login User A ─────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@e2e.com", "password": "AlicePass1!"},
    )
    assert resp.status_code == 200, resp.text
    tokens_a = resp.json()
    token_a = tokens_a["access_token"]
    refresh_token_a = tokens_a["refresh_token"]
    assert token_a
    assert refresh_token_a

    # ── Step 4: Create Organization ──────────────────────────────────────
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": "E2E Organization", "slug": "e2e-org"},
        headers=auth_header(token_a),
    )
    assert resp.status_code == 201, resp.text
    org = resp.json()
    org_id = org["id"]
    assert org["name"] == "E2E Organization"
    assert org["slug"] == "e2e-org"
    assert len(org["members"]) == 1
    assert org["members"][0]["role"] == "OWNER"

    # ── Step 5: Register User B (same tenant) ────────────────────────────
    resp = await client.post(
        "/api/v1/users/",
        json={
            "email": "bob@e2e.com",
            "name": "Bob",
            "password": "BobPass1!",
            "tenant_id": tid,
        },
    )
    assert resp.status_code == 201, resp.text

    # ── Step 6: Login User B ─────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@e2e.com", "password": "BobPass1!"},
    )
    assert resp.status_code == 200, resp.text
    tokens_b = resp.json()
    token_b = tokens_b["access_token"]
    refresh_token_b = tokens_b["refresh_token"]
    user_b_id = get_user_id_from_token(token_b)

    # ── Step 7: Invite User B ────────────────────────────────────────────
    email_sender.clear()  # Ignore welcome emails from registration
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": "bob@e2e.com", "role": "MEMBER"},
        headers=auth_header(token_a),
    )
    assert resp.status_code == 201, resp.text
    inv = resp.json()
    inv_id = inv["id"]
    assert inv["invitee_email"] == "bob@e2e.com"
    assert inv["role"] == "MEMBER"

    # Verify invitation email was sent
    invitation_emails = email_sender.find_by_to("bob@e2e.com")
    assert len(invitation_emails) >= 1

    # ── Step 8: User B accepts invitation ────────────────────────────────
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=auth_header(token_b),
    )
    assert resp.status_code == 200, resp.text
    updated_org = resp.json()
    assert len(updated_org["members"]) == 2
    roles = {m["role"] for m in updated_org["members"]}
    assert roles == {"OWNER", "MEMBER"}

    # ── Step 9: List organizations — both users see the org ──────────────
    resp = await client.get(
        "/api/v1/organizations",
        headers=auth_header(token_a),
    )
    assert resp.status_code == 200, resp.text
    orgs_a = resp.json()
    assert len(orgs_a) == 1
    assert orgs_a[0]["id"] == org_id

    resp = await client.get(
        "/api/v1/organizations",
        headers=auth_header(token_b),
    )
    assert resp.status_code == 200, resp.text
    orgs_b = resp.json()
    assert len(orgs_b) == 1
    assert orgs_b[0]["id"] == org_id

    # ── Step 10: Promote User B to ADMIN ─────────────────────────────────
    resp = await client.patch(
        f"/api/v1/organizations/{org_id}/members/{user_b_id}/role",
        json={"role": "ADMIN"},
        headers=auth_header(token_a),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "ADMIN"

    # ── Step 11: Remove User B ───────────────────────────────────────────
    resp = await client.delete(
        f"/api/v1/organizations/{org_id}/members/{user_b_id}",
        headers=auth_header(token_a),
    )
    assert resp.status_code == 204

    # Verify org now has 1 member
    resp = await client.get(
        "/api/v1/organizations",
        headers=auth_header(token_a),
    )
    assert resp.status_code == 200
    assert len(resp.json()[0]["members"]) == 1

    # ── Step 12: Refresh token rotation ──────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_a},
    )
    assert resp.status_code == 200, resp.text
    new_tokens = resp.json()
    new_access_token = new_tokens["access_token"]
    new_refresh_token = new_tokens["refresh_token"]
    assert new_access_token != token_a  # New access token
    assert new_refresh_token != refresh_token_a  # Rotated refresh token

    # Old refresh token should no longer work
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token_a},
    )
    assert resp.status_code == 401  # Revoked

    # ── Step 13: Logout ──────────────────────────────────────────────────
    resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_refresh_token},
    )
    assert resp.status_code == 204

    # Refresh token should no longer work after logout
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh_token},
    )
    assert resp.status_code == 401
