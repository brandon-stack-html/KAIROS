"""Unit tests for EmailTemplate rendering (build_email)."""

from src.application.shared.email_sender import EmailTemplate, build_email


def test_welcome_contains_user_name():
    msg = build_email(
        EmailTemplate.WELCOME,
        {"to": "alice@example.com", "user_name": "Alice", "app_name": "MySaaS"},
    )
    assert "Alice" in msg.html_body
    assert "Alice" in msg.text_body


def test_welcome_contains_app_name():
    msg = build_email(
        EmailTemplate.WELCOME,
        {"to": "alice@example.com", "user_name": "Alice", "app_name": "MySaaS"},
    )
    assert "MySaaS" in msg.subject
    assert "MySaaS" in msg.text_body


def test_welcome_to_field():
    msg = build_email(
        EmailTemplate.WELCOME,
        {"to": "alice@example.com", "user_name": "Alice", "app_name": "MySaaS"},
    )
    assert msg.to == "alice@example.com"


def test_invitation_contains_accept_url():
    url = "http://localhost:3000/invitations/abc-123/accept"
    msg = build_email(
        EmailTemplate.INVITATION,
        {
            "to": "bob@example.com",
            "inviter_name": "Alice",
            "org_name": "ACME",
            "accept_url": url,
        },
    )
    assert url in msg.html_body
    assert url in msg.text_body


def test_invitation_contains_org_name():
    msg = build_email(
        EmailTemplate.INVITATION,
        {
            "to": "bob@example.com",
            "inviter_name": "Alice",
            "org_name": "ACME Corp",
            "accept_url": "http://example.com/accept",
        },
    )
    assert "ACME Corp" in msg.html_body
    assert "ACME Corp" in msg.text_body


def test_email_message_has_required_fields():
    msg = build_email(
        EmailTemplate.PASSWORD_RESET,
        {"to": "user@example.com", "reset_url": "http://example.com/reset/token"},
    )
    assert msg.to == "user@example.com"
    assert msg.subject
    assert msg.html_body
    assert msg.text_body
    assert msg.from_email is None  # default — sender sets this


def test_extra_context_keys_are_ignored():
    """Extra keys in context must not raise KeyError."""
    msg = build_email(
        EmailTemplate.WELCOME,
        {
            "to": "alice@example.com",
            "user_name": "Alice",
            "app_name": "MySaaS",
            "extra_key": "ignored",
        },
    )
    assert msg.to == "alice@example.com"
