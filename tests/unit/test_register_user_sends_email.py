"""Unit tests — RegisterUserHandler sends welcome email."""

import pytest

from src.application.register_user.command import RegisterUserCommand
from src.application.register_user.handler import RegisterUserHandler
from src.application.shared.email_sender import AbstractEmailSender, EmailMessage
from src.infrastructure.persistence.in_memory.email_sender import InMemoryEmailSender

# ── Minimal in-memory UoW stub ────────────────────────────────────────────────


class _FakeUserRepo:
    def __init__(self):
        self._users = {}

    async def exists_by_email(self, email):
        return email.value in self._users

    async def save(self, user):
        self._users[user.email.value] = user


class _FakeRefreshTokenStore:
    async def save(self, token): ...
    async def find(self, token_id):
        return None

    async def revoke(self, token_id): ...


class _FakeUoW:
    def __init__(self):
        self.users = _FakeUserRepo()
        self.refresh_tokens = _FakeRefreshTokenStore()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def commit(self): ...
    async def rollback(self): ...


class _FakeHasher:
    def hash(self, plain: str) -> str:
        return f"hashed:{plain}"

    def verify(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed:{plain}"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_handler(email_sender: AbstractEmailSender) -> RegisterUserHandler:
    return RegisterUserHandler(
        uow=_FakeUoW(),
        password_hasher=_FakeHasher(),
        email_sender=email_sender,
    )


def _cmd(**overrides) -> RegisterUserCommand:
    defaults = {
        "email": "alice@example.com",
        "name": "Alice",
        "password": "s3cur3",
        "tenant_id": "00000000-0000-4000-8000-000000000001",
        "app_name": "TestSaaS",
    }
    return RegisterUserCommand(**{**defaults, **overrides})


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_successful_registration_sends_welcome_email():
    sender = InMemoryEmailSender()
    handler = _make_handler(sender)

    await handler.handle(_cmd())

    assert len(sender.sent) == 1
    msg = sender.sent[0]
    assert msg.to == "alice@example.com"


@pytest.mark.asyncio
async def test_welcome_email_has_correct_subject():
    sender = InMemoryEmailSender()
    handler = _make_handler(sender)

    await handler.handle(_cmd(app_name="MySaaS"))

    msg = sender.sent[0]
    assert "MySaaS" in msg.subject


@pytest.mark.asyncio
async def test_welcome_email_body_contains_user_name():
    sender = InMemoryEmailSender()
    handler = _make_handler(sender)

    await handler.handle(_cmd(name="Bob"))

    msg = sender.sent[0]
    assert "Bob" in msg.text_body


@pytest.mark.asyncio
async def test_email_sender_failure_does_not_fail_registration():
    """Fire-and-forget: user is saved even when email sender raises."""

    class _BrokenSender(AbstractEmailSender):
        async def send(self, message: EmailMessage) -> None:
            raise RuntimeError("SMTP down")

    handler = _make_handler(_BrokenSender())
    # Should NOT raise:
    user_id = await handler.handle(_cmd())
    assert user_id  # user was created successfully
