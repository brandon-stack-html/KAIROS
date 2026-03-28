"""Unit tests for the Conversation aggregate."""

import pytest

from src.domain.conversation.conversation import Conversation, ConversationType
from src.domain.conversation.errors import InvalidConversationTypeError
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


def _org_id() -> OrganizationId:
    return OrganizationId.generate()


def _project_id() -> ProjectId:
    return ProjectId.generate()


def test_for_organization_creates_org_type():
    conv = Conversation.for_organization(org_id=_org_id())
    assert conv.type is ConversationType.ORG
    assert conv.project_id is None
    assert conv.id is not None


def test_for_project_creates_project_type():
    org = _org_id()
    proj = _project_id()
    conv = Conversation.for_project(org_id=org, project_id=proj)
    assert conv.type is ConversationType.PROJECT
    assert conv.project_id == proj
    assert conv.org_id == org


def test_project_conversation_without_project_id_raises():
    with pytest.raises(InvalidConversationTypeError):
        Conversation(
            id=None,  # type: ignore
            org_id=_org_id(),
            type=ConversationType.PROJECT,
            project_id=None,
        )


def test_org_conversation_with_project_id_raises():
    with pytest.raises(InvalidConversationTypeError):
        Conversation(
            id=None,  # type: ignore
            org_id=_org_id(),
            type=ConversationType.ORG,
            project_id=_project_id(),
        )


def test_two_conversations_have_different_ids():
    c1 = Conversation.for_organization(_org_id())
    c2 = Conversation.for_organization(_org_id())
    assert c1.id != c2.id
