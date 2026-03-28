"""Unit tests for the Message aggregate."""

import pytest

from src.domain.message.errors import InvalidMessageContentError
from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId
from src.domain.user.user import UserId


def _make_message(content: str = "Hello, world!") -> Message:
    return Message.create(
        conversation_id=ConversationId.generate(),
        sender_id=UserId(str(__import__("uuid").uuid4())),
        content=content,
    )


def test_create_message_success():
    msg = _make_message("Hi there!")
    assert msg.content == "Hi there!"
    assert msg.id is not None


def test_content_is_stripped():
    msg = _make_message("  trimmed  ")
    assert msg.content == "trimmed"


def test_empty_content_raises():
    with pytest.raises(InvalidMessageContentError):
        _make_message("")


def test_whitespace_only_raises():
    with pytest.raises(InvalidMessageContentError):
        _make_message("   ")


def test_content_at_max_length_succeeds():
    msg = _make_message("x" * 4000)
    assert len(msg.content) == 4000


def test_content_exceeding_max_raises():
    with pytest.raises(InvalidMessageContentError):
        _make_message("x" * 4001)


def test_two_messages_have_different_ids():
    m1 = _make_message("a")
    m2 = _make_message("b")
    assert m1.id != m2.id
