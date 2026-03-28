"""Driven port for the Conversation bounded context."""

from abc import ABC, abstractmethod

from src.domain.conversation.conversation import Conversation
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


class IConversationRepository(ABC):
    @abstractmethod
    async def save(self, conversation: Conversation) -> None: ...

    @abstractmethod
    async def find_by_id(
        self, conversation_id: ConversationId
    ) -> Conversation | None: ...

    @abstractmethod
    async def find_by_org(
        self, org_id: OrganizationId
    ) -> list[Conversation]: ...

    @abstractmethod
    async def find_by_project(
        self, project_id: ProjectId
    ) -> Conversation | None: ...
