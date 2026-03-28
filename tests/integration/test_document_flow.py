"""Integration tests — Document Management flow.

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


def _pdf_upload(filename: str = "test.pdf") -> tuple:
    """Returns (files, content) suitable for httpx multipart upload."""
    content = b"%PDF-1.4 fake pdf content"
    files = {"file": (filename, content, "application/pdf")}
    return files, content


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_upload_org_document(db_session: AsyncSession, client: AsyncClient):
    """User uploads a document to an org — 201, correct response fields."""
    tid = await _provision_tenant(db_session, "DocCorp A", "doccorp-a")
    token = await _register_and_login(client, tid, "owner@doc-a.com")
    org_id = await _create_org(client, token, name="Doc Corp A", slug="doc-corp-a")

    files, content = _pdf_upload("report.pdf")
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/documents",
        files=files,
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["filename"] == "report.pdf"
    assert data["file_type"] == "application/pdf"
    assert data["file_size_bytes"] == len(content)
    assert data["org_id"] == org_id
    assert data["project_id"] is None
    assert "id" in data


@pytest.mark.asyncio
async def test_list_org_documents(db_session: AsyncSession, client: AsyncClient):
    """After uploading two docs, list returns both."""
    tid = await _provision_tenant(db_session, "DocCorp B", "doccorp-b")
    token = await _register_and_login(client, tid, "owner@doc-b.com")
    org_id = await _create_org(client, token, name="Doc Corp B", slug="doc-corp-b")

    for i in range(2):
        files, _ = _pdf_upload(f"file-{i}.pdf")
        await client.post(
            f"/api/v1/organizations/{org_id}/documents",
            files=files,
            headers=_auth(token),
        )

    resp = await client.get(
        f"/api/v1/organizations/{org_id}/documents",
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_delete_own_document(db_session: AsyncSession, client: AsyncClient):
    """Uploader can delete their own document."""
    tid = await _provision_tenant(db_session, "DocCorp C", "doccorp-c")
    token = await _register_and_login(client, tid, "owner@doc-c.com")
    org_id = await _create_org(client, token, name="Doc Corp C", slug="doc-corp-c")

    files, _ = _pdf_upload("deleteme.pdf")
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/documents",
        files=files,
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    doc_id = resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/documents/{doc_id}",
        headers=_auth(token),
    )
    assert resp.status_code == 204, resp.text

    # Confirm it's gone
    resp = await client.get(
        f"/api/v1/organizations/{org_id}/documents",
        headers=_auth(token),
    )
    assert resp.json() == []


@pytest.mark.asyncio
async def test_upload_invalid_file_type_returns_400(
    db_session: AsyncSession, client: AsyncClient
):
    """Uploading a disallowed MIME type returns 400."""
    tid = await _provision_tenant(db_session, "DocCorp D", "doccorp-d")
    token = await _register_and_login(client, tid, "owner@doc-d.com")
    org_id = await _create_org(client, token, name="Doc Corp D", slug="doc-corp-d")

    files = {"file": ("malware.exe", b"MZ", "application/x-executable")}
    resp = await client.post(
        f"/api/v1/organizations/{org_id}/documents",
        files=files,
        headers=_auth(token),
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.asyncio
async def test_get_document_metadata_via_download_404(
    db_session: AsyncSession, client: AsyncClient
):
    """Downloading non-existent document returns 404."""
    tid = await _provision_tenant(db_session, "DocCorp E", "doccorp-e")
    token = await _register_and_login(client, tid, "owner@doc-e.com")

    resp = await client.get(
        "/api/v1/documents/00000000-0000-0000-0000-000000000000/download",
        headers=_auth(token),
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_unauthenticated_cannot_upload(db_session: AsyncSession, client: AsyncClient):
    """Request without JWT gets 401."""
    files, _ = _pdf_upload()
    resp = await client.post(
        "/api/v1/organizations/some-org/documents",
        files=files,
    )
    assert resp.status_code == 401, resp.text
