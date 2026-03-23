"""Project aggregate root.

Domain rules enforced here:
- Name: 2–100 characters (stripped).
- create() sets status to ACTIVE by default.

NOT frozen — SQLAlchemy imperative mapper sets attributes on reconstruction.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.project.errors import InvalidProjectNameError
from src.domain.project.events import ProjectCreated
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class ProjectStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


@dataclass(eq=False)
class Project(AggregateRoot):
    """Project aggregate root.

    Field order for @dataclass inheritance:
      id          – inherited from Entity (required)
      _domain_events – AggregateRoot (init=False)
      name / description / org_id / tenant_id – required
      status / created_at – optional (have defaults)
    """

    id: ProjectId
    name: str
    description: str
    org_id: OrganizationId
    tenant_id: TenantId
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate_name(self.name)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        org_id: OrganizationId,
        tenant_id: TenantId,
        owner_id: str,
    ) -> "Project":
        name = name.strip()
        cls._validate_name(name)

        project = cls(
            id=ProjectId.generate(),
            name=name,
            description=description,
            org_id=org_id,
            tenant_id=tenant_id,
        )

        project.add_domain_event(
            ProjectCreated(
                project_id=project.id.value,
                name=project.name,
                org_id=org_id.value,
                tenant_id=tenant_id.value,
                owner_id=owner_id,
            )
        )
        return project

    # ── Validation helpers ────────────────────────────────────────────────

    @staticmethod
    def _validate_name(name: str) -> None:
        if not (2 <= len(name) <= 100):
            raise InvalidProjectNameError(name)
