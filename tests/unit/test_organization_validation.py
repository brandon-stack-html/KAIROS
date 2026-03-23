"""Unit tests — Organization name/slug validation + Role enum methods.

Pure domain tests — no database, no HTTP, no async.
"""

import pytest

from src.domain.organization.errors import InvalidOrgNameError, InvalidOrgSlugError
from src.domain.organization.organization import Organization
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


def _make_org(name: str = "Acme Corp", slug: str = "acme-corp") -> Organization:
    """Helper to create an Organization via the factory."""
    return Organization.create(
        name=name,
        slug=slug,
        owner_id=UserId("owner-001"),
        tenant_id=TenantId.from_str("00000000-0000-4000-8000-000000000001"),
    )


# ── Organization name validation ─────────────────────────────────────────────


class TestOrgNameValidation:
    def test_valid_org_name(self):
        org = _make_org(name="Acme Corp")
        assert org.name == "Acme Corp"

    def test_org_name_too_short_raises(self):
        with pytest.raises(InvalidOrgNameError):
            _make_org(name="A")

    def test_org_name_too_long_raises(self):
        with pytest.raises(InvalidOrgNameError):
            _make_org(name="A" * 101)

    def test_org_name_stripped(self):
        org = _make_org(name="  Acme  ")
        assert org.name == "Acme"


# ── Organization slug validation ─────────────────────────────────────────────


class TestOrgSlugValidation:
    def test_valid_slug(self):
        org = _make_org(slug="my-org-123")
        assert org.slug == "my-org-123"

    def test_slug_uppercase_normalized(self):
        org = _make_org(slug="My-Org")
        assert org.slug == "my-org"

    def test_slug_starts_with_hyphen_raises(self):
        with pytest.raises(InvalidOrgSlugError):
            _make_org(slug="-bad")

    def test_slug_ends_with_hyphen_raises(self):
        with pytest.raises(InvalidOrgSlugError):
            _make_org(slug="bad-")

    def test_slug_special_chars_raises(self):
        with pytest.raises(InvalidOrgSlugError):
            _make_org(slug="has space")

    def test_slug_underscore_raises(self):
        with pytest.raises(InvalidOrgSlugError):
            _make_org(slug="has_under")


# ── Role enum ────────────────────────────────────────────────────────────────


class TestRole:
    def test_owner_can_invite(self):
        assert Role.OWNER.can_invite() is True

    def test_admin_can_invite(self):
        assert Role.ADMIN.can_invite() is True

    def test_member_cannot_invite(self):
        assert Role.MEMBER.can_invite() is False

    def test_owner_can_delete_org(self):
        assert Role.OWNER.can_delete_org() is True

    def test_admin_cannot_delete_org(self):
        assert Role.ADMIN.can_delete_org() is False

    def test_member_cannot_delete_org(self):
        assert Role.MEMBER.can_delete_org() is False
