"""Deliverable aggregate root.

Domain rules enforced here:
- Title: 2–100 characters.
- url_link: non-empty.
- approve() / request_changes() only allowed when status is PENDING.

NOT frozen — SQLAlchemy imperative mapper sets attributes on reconstruction.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.deliverable.errors import (
    DeliverableAlreadyReviewedError,
    InvalidDeliverableTitleError,
    InvalidDeliverableUrlError,
)
from src.domain.deliverable.events import (
    ChangesRequested,
    DeliverableApproved,
    DeliverableSubmitted,
)
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId


class DeliverableStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


@dataclass(eq=False)
class Deliverable(AggregateRoot):
    """Deliverable aggregate root.

    Field order for @dataclass inheritance:
      id            – inherited from Entity (required)
      _domain_events – AggregateRoot (init=False)
      title / url_link / project_id / tenant_id – required
      status / created_at / updated_at – optional (have defaults)
    """

    id: DeliverableId
    title: str
    url_link: str
    project_id: ProjectId
    tenant_id: TenantId
    status: DeliverableStatus = field(default=DeliverableStatus.PENDING)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self._validate_title(self.title)
        self._validate_url(self.url_link)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        title: str,
        url_link: str,
        project_id: ProjectId,
        tenant_id: TenantId,
        submitted_by: str,
    ) -> "Deliverable":
        title = title.strip()
        cls._validate_title(title)
        cls._validate_url(url_link)

        now = datetime.now(UTC)
        deliverable = cls(
            id=DeliverableId.generate(),
            title=title,
            url_link=url_link,
            project_id=project_id,
            tenant_id=tenant_id,
            created_at=now,
            updated_at=now,
        )

        deliverable.add_domain_event(
            DeliverableSubmitted(
                deliverable_id=deliverable.id.value,
                title=deliverable.title,
                project_id=project_id.value,
                tenant_id=tenant_id.value,
                submitted_by=submitted_by,
            )
        )
        return deliverable

    # ── Behaviour ─────────────────────────────────────────────────────────

    def approve(self, approver_id: str) -> None:
        if self.status is not DeliverableStatus.PENDING:
            raise DeliverableAlreadyReviewedError()
        self.status = DeliverableStatus.APPROVED
        self.updated_at = datetime.now(UTC)
        self.add_domain_event(
            DeliverableApproved(
                deliverable_id=self.id.value,
                project_id=self.project_id.value,
                tenant_id=self.tenant_id.value,
                approved_by=approver_id,
            )
        )

    def request_changes(self, reviewer_id: str) -> None:
        if self.status is not DeliverableStatus.PENDING:
            raise DeliverableAlreadyReviewedError()
        self.status = DeliverableStatus.CHANGES_REQUESTED
        self.updated_at = datetime.now(UTC)
        self.add_domain_event(
            ChangesRequested(
                deliverable_id=self.id.value,
                project_id=self.project_id.value,
                tenant_id=self.tenant_id.value,
                reviewed_by=reviewer_id,
            )
        )

    # ── Validation helpers ────────────────────────────────────────────────

    @staticmethod
    def _validate_title(title: str) -> None:
        if not (2 <= len(title) <= 100):
            raise InvalidDeliverableTitleError(title)

    @staticmethod
    def _validate_url(url_link: str) -> None:
        if not url_link or not url_link.strip():
            raise InvalidDeliverableUrlError()
