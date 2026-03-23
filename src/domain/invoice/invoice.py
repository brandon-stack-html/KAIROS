"""Invoice aggregate root.

Domain rules enforced here:
- Title: 2–100 characters.
- Amount: must be positive (> 0).
- mark_paid() only allowed when status is not already PAID.

NOT frozen — SQLAlchemy imperative mapper sets attributes on reconstruction.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from src.domain.invoice.errors import (
    InvalidInvoiceAmountError,
    InvalidInvoiceTitleError,
    InvoiceAlreadyPaidError,
)
from src.domain.invoice.events import InvoiceIssued, InvoicePaid
from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.invoice_id import InvoiceId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId


class InvoiceStatus(StrEnum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"


@dataclass(eq=False)
class Invoice(AggregateRoot):
    """Invoice aggregate root."""

    id: InvoiceId
    title: str
    amount: Decimal
    org_id: OrganizationId
    tenant_id: TenantId
    status: InvoiceStatus = field(default=InvoiceStatus.DRAFT)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    paid_at: datetime | None = field(default=None)

    def __post_init__(self) -> None:
        self._validate_title(self.title)
        self._validate_amount(self.amount)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        title: str,
        amount: Decimal,
        org_id: OrganizationId,
        tenant_id: TenantId,
        issued_by: str,
    ) -> "Invoice":
        title = title.strip()
        cls._validate_title(title)
        cls._validate_amount(amount)

        invoice = cls(
            id=InvoiceId.generate(),
            title=title,
            amount=amount,
            org_id=org_id,
            tenant_id=tenant_id,
            created_at=datetime.now(UTC),
        )

        invoice.add_domain_event(
            InvoiceIssued(
                invoice_id=invoice.id.value,
                title=invoice.title,
                amount=str(amount),
                org_id=org_id.value,
                tenant_id=tenant_id.value,
                issued_by=issued_by,
            )
        )
        return invoice

    # ── Behaviour ─────────────────────────────────────────────────────────

    def mark_paid(self) -> None:
        if self.status is InvoiceStatus.PAID:
            raise InvoiceAlreadyPaidError()
        self.status = InvoiceStatus.PAID
        self.paid_at = datetime.now(UTC)
        self.add_domain_event(
            InvoicePaid(
                invoice_id=self.id.value,
                org_id=self.org_id.value,
                tenant_id=self.tenant_id.value,
            )
        )

    # ── Validation helpers ────────────────────────────────────────────────

    @staticmethod
    def _validate_title(title: str) -> None:
        if not (2 <= len(title) <= 100):
            raise InvalidInvoiceTitleError(title)

    @staticmethod
    def _validate_amount(amount: object) -> None:
        try:
            if Decimal(str(amount)) <= 0:
                raise InvalidInvoiceAmountError(amount)
        except Exception as exc:
            if isinstance(exc, InvalidInvoiceAmountError):
                raise
            raise InvalidInvoiceAmountError(amount) from exc
