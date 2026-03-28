from dataclasses import dataclass


@dataclass(frozen=True)
class ListDocumentsCommand:
    org_id: str | None = None
    project_id: str | None = None
