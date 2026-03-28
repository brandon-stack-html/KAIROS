from dataclasses import dataclass


@dataclass(frozen=True)
class CreateConversationCommand:
    org_id: str
    project_id: str | None = None  # None → ORG type; set → PROJECT type
