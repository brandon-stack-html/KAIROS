"""Unit tests for all messaging use case handlers.

Uses lightweight in-memory fakes — no DB, no HTTP.
"""

import uuid

import pytest

from src.application.create_conversation.command import CreateConversationCommand
from src.application.create_conversation.handler import CreateConversationHandler
from src.application.delete_message.command import DeleteMessageCommand
from src.application.delete_message.handler import DeleteMessageHandler
from src.application.get_conversation.command import GetConversationCommand
from src.application.get_conversation.handler import GetConversationHandler
from src.application.list_messages.command import ListMessagesCommand
from src.application.list_messages.handler import ListMessagesHandler
from src.application.list_org_conversations.command import ListOrgConversationsCommand
from src.application.list_org_conversations.handler import ListOrgConversationsHandler
from src.application.send_message.command import SendMessageCommand
from src.application.send_message.handler import SendMessageHandler
from src.domain.conversation.conversation import Conversation, ConversationType
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.conversation.repository import IConversationRepository
from src.domain.message.errors import MessageNotFoundError, MessageNotOwnedError
from src.domain.message.message import Message
from src.domain.message.repository import IMessageRepository
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.message_id import MessageId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


# ── In-memory fakes ────────────────────────────────────────────────────────────


class FakeConversationRepo(IConversationRepository):
    def __init__(self) -> None:
        self._store: dict[str, Conversation] = {}

    async def save(self, conversation: Conversation) -> None:
        self._store[conversation.id.value] = conversation

    async def find_by_id(self, conversation_id: ConversationId) -> Conversation | None:
        return self._store.get(conversation_id.value)

    async def find_by_org(self, org_id: OrganizationId) -> list[Conversation]:
        return [c for c in self._store.values() if c.org_id == org_id]

    async def find_by_project(self, project_id: ProjectId) -> Conversation | None:
        return next(
            (c for c in self._store.values() if c.project_id == project_id), None
        )


class FakeMessageRepo(IMessageRepository):
    def __init__(self) -> None:
        self._store: dict[str, Message] = {}

    async def save(self, message: Message) -> None:
        self._store[message.id.value] = message

    async def find_by_id(self, message_id: MessageId) -> Message | None:
        return self._store.get(message_id.value)

    async def find_by_conversation(
        self,
        conversation_id: ConversationId,
        *,
        page: int,
        limit: int,
    ) -> list[Message]:
        msgs = [
            m for m in self._store.values()
            if m.conversation_id == conversation_id
        ]
        msgs.sort(key=lambda m: m.created_at)
        offset = (page - 1) * limit
        return msgs[offset : offset + limit]

    async def delete(self, message_id: MessageId) -> None:
        self._store.pop(message_id.value, None)


class FakeUoW:
    """Minimal async context manager that holds fake repos."""

    def __init__(
        self,
        conv_repo: FakeConversationRepo | None = None,
        msg_repo: FakeMessageRepo | None = None,
    ) -> None:
        self.conversations = conv_repo or FakeConversationRepo()
        self.messages = msg_repo or FakeMessageRepo()
        self._committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._committed = True

    async def commit(self) -> None:
        self._committed = True

    async def rollback(self) -> None:
        pass


# ── Helpers ────────────────────────────────────────────────────────────────────


def _uid() -> str:
    return str(uuid.uuid4())


# ── CreateConversationHandler ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_org_conversation():
    uow = FakeUoW()
    handler = CreateConversationHandler(uow=uow)
    org_id = _uid()
    conv = await handler.handle(CreateConversationCommand(org_id=org_id))
    assert conv.type is ConversationType.ORG
    assert conv.project_id is None
    assert uow._committed


@pytest.mark.asyncio
async def test_create_project_conversation():
    uow = FakeUoW()
    handler = CreateConversationHandler(uow=uow)
    proj_id = _uid()
    conv = await handler.handle(
        CreateConversationCommand(org_id=_uid(), project_id=proj_id)
    )
    assert conv.type is ConversationType.PROJECT
    assert conv.project_id.value == proj_id


# ── GetConversationHandler ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_conversation_found():
    conv_repo = FakeConversationRepo()
    existing = Conversation.for_organization(OrganizationId.generate())
    await conv_repo.save(existing)

    uow = FakeUoW(conv_repo=conv_repo)
    handler = GetConversationHandler(uow=uow)
    result = await handler.handle(
        GetConversationCommand(conversation_id=existing.id.value)
    )
    assert result.id == existing.id


@pytest.mark.asyncio
async def test_get_conversation_not_found():
    uow = FakeUoW()
    handler = GetConversationHandler(uow=uow)
    with pytest.raises(ConversationNotFoundError):
        await handler.handle(GetConversationCommand(conversation_id=_uid()))


# ── ListOrgConversationsHandler ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_org_conversations():
    conv_repo = FakeConversationRepo()
    org_id = OrganizationId.generate()
    other_org = OrganizationId.generate()

    c1 = Conversation.for_organization(org_id)
    c2 = Conversation.for_organization(org_id)
    c3 = Conversation.for_organization(other_org)
    for c in (c1, c2, c3):
        await conv_repo.save(c)

    uow = FakeUoW(conv_repo=conv_repo)
    handler = ListOrgConversationsHandler(uow=uow)
    result = await handler.handle(
        ListOrgConversationsCommand(org_id=org_id.value)
    )
    assert len(result) == 2
    ids = {c.id.value for c in result}
    assert c1.id.value in ids
    assert c2.id.value in ids


# ── SendMessageHandler ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_message_success():
    conv_repo = FakeConversationRepo()
    conv = Conversation.for_organization(OrganizationId.generate())
    await conv_repo.save(conv)

    msg_repo = FakeMessageRepo()
    uow = FakeUoW(conv_repo=conv_repo, msg_repo=msg_repo)
    handler = SendMessageHandler(uow=uow)

    sender_id = _uid()
    msg = await handler.handle(
        SendMessageCommand(
            conversation_id=conv.id.value,
            sender_id=sender_id,
            content="Hello!",
        )
    )
    assert msg.content == "Hello!"
    assert msg.sender_id.value == sender_id
    assert msg.conversation_id == conv.id


@pytest.mark.asyncio
async def test_send_message_conversation_not_found():
    uow = FakeUoW()
    handler = SendMessageHandler(uow=uow)
    with pytest.raises(ConversationNotFoundError):
        await handler.handle(
            SendMessageCommand(
                conversation_id=_uid(),
                sender_id=_uid(),
                content="Hi",
            )
        )


# ── DeleteMessageHandler ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_message_by_owner():
    conv_repo = FakeConversationRepo()
    conv = Conversation.for_organization(OrganizationId.generate())
    await conv_repo.save(conv)

    msg_repo = FakeMessageRepo()
    sender_id = _uid()

    from src.domain.message.message import Message
    from src.domain.shared.conversation_id import ConversationId
    from src.domain.user.user import UserId

    msg = Message.create(
        conversation_id=conv.id,
        sender_id=UserId(sender_id),
        content="to delete",
    )
    await msg_repo.save(msg)

    uow = FakeUoW(conv_repo=conv_repo, msg_repo=msg_repo)
    handler = DeleteMessageHandler(uow=uow)
    await handler.handle(
        DeleteMessageCommand(message_id=msg.id.value, requester_id=sender_id)
    )
    assert await msg_repo.find_by_id(msg.id) is None


@pytest.mark.asyncio
async def test_delete_message_not_owned_raises():
    conv_repo = FakeConversationRepo()
    conv = Conversation.for_organization(OrganizationId.generate())
    await conv_repo.save(conv)

    msg_repo = FakeMessageRepo()
    from src.domain.message.message import Message
    from src.domain.user.user import UserId

    msg = Message.create(
        conversation_id=conv.id,
        sender_id=UserId(_uid()),
        content="not mine",
    )
    await msg_repo.save(msg)

    uow = FakeUoW(conv_repo=conv_repo, msg_repo=msg_repo)
    handler = DeleteMessageHandler(uow=uow)
    with pytest.raises(MessageNotOwnedError):
        await handler.handle(
            DeleteMessageCommand(
                message_id=msg.id.value,
                requester_id=_uid(),  # different user
            )
        )


@pytest.mark.asyncio
async def test_delete_message_not_found_raises():
    uow = FakeUoW()
    handler = DeleteMessageHandler(uow=uow)
    with pytest.raises(MessageNotFoundError):
        await handler.handle(
            DeleteMessageCommand(message_id=_uid(), requester_id=_uid())
        )


# ── ListMessagesHandler ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_messages_paginated():
    conv_repo = FakeConversationRepo()
    conv = Conversation.for_organization(OrganizationId.generate())
    await conv_repo.save(conv)

    msg_repo = FakeMessageRepo()
    from src.domain.message.message import Message
    from src.domain.user.user import UserId

    for i in range(5):
        await msg_repo.save(
            Message.create(
                conversation_id=conv.id,
                sender_id=UserId(_uid()),
                content=f"msg {i}",
            )
        )

    uow = FakeUoW(conv_repo=conv_repo, msg_repo=msg_repo)
    handler = ListMessagesHandler(uow=uow)

    page1 = await handler.handle(
        ListMessagesCommand(conversation_id=conv.id.value, page=1, limit=3)
    )
    assert len(page1) == 3

    page2 = await handler.handle(
        ListMessagesCommand(conversation_id=conv.id.value, page=2, limit=3)
    )
    assert len(page2) == 2


@pytest.mark.asyncio
async def test_list_messages_conversation_not_found():
    uow = FakeUoW()
    handler = ListMessagesHandler(uow=uow)
    with pytest.raises(ConversationNotFoundError):
        await handler.handle(
            ListMessagesCommand(conversation_id=_uid(), page=1, limit=50)
        )
