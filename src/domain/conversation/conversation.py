"""Conversation aggregate root.

Domain rules:
- A PROJECT conversation must have a project_id.
- An ORG conversation must NOT have a project_id.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.conversation.errors import InvalidConversationTypeError
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


class ConversationType(StrEnum):
    ORG = "ORG"
    PROJECT = "PROJECT"


@dataclass(eq=False)
class Conversation(AggregateRoot):
    """Conversation aggregate root."""

    id: ConversationId
    org_id: OrganizationId
    type: ConversationType
    project_id: ProjectId | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if self.type is ConversationType.PROJECT and self.project_id is None:
            raise InvalidConversationTypeError(
                "A PROJECT conversation requires a project_id."
            )
        if self.type is ConversationType.ORG and self.project_id is not None:
            raise InvalidConversationTypeError(
                "An ORG conversation must not have a project_id."
            )

    @classmethod
    def for_organization(cls, org_id: OrganizationId) -> "Conversation":
        return cls(
            id=ConversationId.generate(),
            org_id=org_id,
            type=ConversationType.ORG,
            project_id=None,
        )

    @classmethod
    def for_project(
        cls, org_id: OrganizationId, project_id: ProjectId
    ) -> "Conversation":
        return cls(
            id=ConversationId.generate(),
            org_id=org_id,
            type=ConversationType.PROJECT,
            project_id=project_id,
        )
