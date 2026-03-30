"""Unit tests for ExtractActionItemsHandler."""

import pytest

from src.application.extract_action_items.command import ExtractActionItemsCommand
from src.application.extract_action_items.handler import ExtractActionItemsHandler
from src.domain.conversation.conversation import Conversation
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.message_id import MessageId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId
from src.infrastructure.persistence.in_memory.ai_service import InMemoryAiService
from uuid import uuid4


class FakeConversationRepo:
    def __init__(self, conversation: Conversation | None = None):
        self._conversation = conversation

    async def find_by_id(self, conversation_id):
        return self._conversation

    async def save(self, conversation):
        pass

    async def find_by_org(self, org_id):
        return []

    async def find_by_project(self, project_id):
        return None


class FakeMessageRepo:
    def __init__(self, messages: list[Message] | None = None):
        self._messages = messages or []

    async def find_by_conversation(self, conversation_id, *, page, limit):
        return self._messages

    async def find_by_id(self, message_id):
        return None

    async def delete(self, message_id):
        pass

    async def save(self, message):
        pass


class FakeMessagingUoW:
    def __init__(
        self,
        conversation: Conversation | None = None,
        messages: list[Message] | None = None,
    ):
        self.conversations = FakeConversationRepo(conversation)
        self.messages = FakeMessageRepo(messages)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


def make_conversation(org_id: str = None) -> Conversation:
    """Create a test conversation."""
    return Conversation.for_organization(
        org_id=OrganizationId(org_id or str(uuid4()))
    )


def make_message(sender_id: str = None, content: str = "Test message") -> Message:
    """Create a test message."""
    return Message.create(
        conversation_id=ConversationId.generate(),
        sender_id=UserId(sender_id or str(uuid4())),
        content=content,
    )


def make_command(conversation_id: str = "c1") -> ExtractActionItemsCommand:
    """Create a test command."""
    return ExtractActionItemsCommand(
        conversation_id=conversation_id,
        user_id=str(uuid4()),
        tenant_id=str(uuid4()),
    )


class TestExtractActionItemsHandler:
    """Unit tests for ExtractActionItemsHandler."""

    @pytest.mark.asyncio
    async def test_returns_ai_response_with_messages(self):
        """Should return AI-extracted action items when messages exist."""
        # Arrange
        ai = InMemoryAiService()
        ai.response = '{"action_items":[{"task":"implement auth","assigned_to":"user123","deadline":"next week","priority":"high","source_quote":"I\'ll implement auth"}],"summary":"team needs auth implemented"}'

        messages = [
            make_message(content="I'll implement auth by next week"),
            make_message(content="Great, let's get started"),
        ]
        conversation = make_conversation()
        uow = FakeMessagingUoW(conversation=conversation, messages=messages)
        handler = ExtractActionItemsHandler(uow, ai)
        command = make_command()

        # Act
        result = await handler.handle(command)

        # Assert
        assert "action_items" in result
        assert "implement auth" in result
        assert len(ai.calls) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_messages(self):
        """Should return empty JSON without calling AI when no messages exist."""
        # Arrange
        ai = InMemoryAiService()
        conversation = make_conversation()
        uow = FakeMessagingUoW(conversation=conversation, messages=[])
        handler = ExtractActionItemsHandler(uow, ai)
        command = make_command()

        # Act
        result = await handler.handle(command)

        # Assert
        assert '"action_items": []' in result
        assert len(ai.calls) == 0  # AI not called

    @pytest.mark.asyncio
    async def test_raises_not_found_when_conversation_missing(self):
        """Should raise ConversationNotFoundError if conversation does not exist."""
        # Arrange
        ai = InMemoryAiService()
        uow = FakeMessagingUoW(conversation=None, messages=[])
        handler = ExtractActionItemsHandler(uow, ai)
        command = make_command()

        # Act & Assert
        with pytest.raises(ConversationNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_includes_messages_in_prompt(self):
        """Should include message content in the prompt sent to AI."""
        # Arrange
        ai = InMemoryAiService()
        ai.response = '{"action_items":[],"summary":"test"}'

        message_content = "Can you review the design by Friday?"
        messages = [make_message(content=message_content)]
        conversation = make_conversation()
        uow = FakeMessagingUoW(conversation=conversation, messages=messages)
        handler = ExtractActionItemsHandler(uow, ai)
        command = make_command()

        # Act
        await handler.handle(command)

        # Assert
        assert len(ai.calls) == 1
        prompt = ai.calls[0]["prompt"]
        assert message_content in prompt
