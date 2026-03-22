"""Shared test helpers — reusable across integration, e2e, and unit tests.

These are plain async functions (not fixtures) so they compose cleanly
in sequential E2E tests and reduce duplication across test files.
"""
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.tenant.tenant import Tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)


def auth_header(token: str) -> dict:
    """Return an Authorization header dict for the given JWT."""
    return {"Authorization": f"Bearer {token}"}


def get_user_id_from_token(token: str) -> str:
    """Decode a JWT and return the 'sub' (user_id) claim."""
    from src.infrastructure.security.jwt_handler import decode_token

    return decode_token(token)["sub"]


async def provision_tenant(
    db_session: AsyncSession, name: str = "Test Corp", slug: str = "test-corp"
) -> str:
    """Create a tenant directly via the repository and return its id string."""
    repo = SqlAlchemyTenantRepository(db_session)
    tenant = Tenant.provision(name=name, slug=slug)
    await repo.save(tenant)
    await db_session.commit()
    return tenant.id.value


async def register_user(
    client: AsyncClient,
    tenant_id: str,
    email: str,
    password: str = "Password1!",
    name: str = "Test User",
) -> dict:
    """POST /api/v1/users/ — asserts 201, returns response JSON."""
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
    return resp.json()


async def login_user(
    client: AsyncClient,
    email: str,
    password: str = "Password1!",
) -> dict:
    """POST /api/v1/auth/login — asserts 200, returns response JSON with tokens."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


async def register_and_login(
    client: AsyncClient,
    tenant_id: str,
    email: str,
    password: str = "Password1!",
    name: str = "Test User",
) -> str:
    """Register + login, return the access_token."""
    await register_user(client, tenant_id, email, password, name)
    tokens = await login_user(client, email, password)
    return tokens["access_token"]


async def create_org(
    client: AsyncClient,
    token: str,
    name: str,
    slug: str,
) -> dict:
    """POST /api/v1/organizations — asserts 201, returns org JSON."""
    resp = await client.post(
        "/api/v1/organizations",
        json={"name": name, "slug": slug},
        headers=auth_header(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def invite_member(
    client: AsyncClient,
    token: str,
    org_id: str,
    email: str,
    role: str = "MEMBER",
) -> dict:
    """POST /api/v1/organizations/{id}/invitations — asserts 201, returns invitation JSON."""
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations",
        json={"email": email, "role": role},
        headers=auth_header(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def accept_invitation(
    client: AsyncClient,
    token: str,
    org_id: str,
    inv_id: str,
) -> dict:
    """POST /api/v1/organizations/{id}/invitations/{inv_id}/accept — asserts 200."""
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/invitations/{inv_id}/accept",
        headers=auth_header(token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()
