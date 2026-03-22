"""Unit tests — User value object validation (Email, Name, UserId).

Pure domain tests — no database, no HTTP, no async.
"""
import pytest

from src.domain.user.errors import InvalidEmailError, InvalidUserNameError
from src.domain.user.user import UserEmail, UserId, UserName


# ── UserEmail ────────────────────────────────────────────────────────────────


class TestUserEmail:
    def test_valid_email_accepted(self):
        email = UserEmail("alice@example.com")
        assert email.value == "alice@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(InvalidEmailError):
            UserEmail("not-an-email")

    def test_email_missing_domain_raises(self):
        with pytest.raises(InvalidEmailError):
            UserEmail("foo@")

    def test_email_missing_at_raises(self):
        with pytest.raises(InvalidEmailError):
            UserEmail("foo.com")

    def test_email_equality_by_value(self):
        assert UserEmail("a@b.com") == UserEmail("a@b.com")


# ── UserName ─────────────────────────────────────────────────────────────────


class TestUserName:
    def test_valid_name_accepted(self):
        name = UserName("Al")
        assert name.value == "Al"

    def test_name_too_short_raises(self):
        with pytest.raises(InvalidUserNameError):
            UserName("A")

    def test_name_too_long_raises(self):
        with pytest.raises(InvalidUserNameError):
            UserName("A" * 101)

    def test_name_strips_whitespace(self):
        name = UserName("  Alice  ")
        assert name.value == "Alice"


# ── UserId ───────────────────────────────────────────────────────────────────


class TestUserId:
    def test_equality_by_value(self):
        assert UserId("abc-123") == UserId("abc-123")

    def test_different_values_not_equal(self):
        assert UserId("abc-123") != UserId("xyz-789")
