"""Unit tests for the Invoice aggregate."""

import uuid
from decimal import Decimal

import pytest

from src.domain.invoice.errors import InvalidInvoiceAmountError, InvoiceAlreadyPaidError
from src.domain.invoice.events import InvoiceIssued, InvoicePaid
from src.domain.invoice.invoice import Invoice, InvoiceStatus
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId


def _make_invoice(
    title: str = "Website Project",
    amount: Decimal = Decimal("99.99"),
) -> Invoice:
    return Invoice.create(
        title=title,
        amount=amount,
        org_id=OrganizationId.generate(),
        tenant_id=TenantId(str(uuid.uuid4())),
        issued_by=str(uuid.uuid4()),
    )


def test_create_emits_invoice_issued():
    inv = _make_invoice()
    events = inv.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], InvoiceIssued)


def test_create_event_amount_is_string():
    inv = _make_invoice(amount=Decimal("99.99"))
    event = inv.pull_domain_events()[0]
    assert isinstance(event, InvoiceIssued)
    assert event.amount == "99.99"
    assert isinstance(event.amount, str)


def test_amount_zero_raises_error():
    with pytest.raises(InvalidInvoiceAmountError):
        _make_invoice(amount=Decimal("0"))


def test_amount_negative_raises_error():
    with pytest.raises(InvalidInvoiceAmountError):
        _make_invoice(amount=Decimal("-10.00"))


def test_amount_valid_decimal():
    inv = _make_invoice(amount=Decimal("99.99"))
    assert inv.amount == Decimal("99.99")


def test_default_status_is_draft():
    inv = _make_invoice()
    assert inv.status is InvoiceStatus.DRAFT


def test_mark_paid_changes_status_and_sets_paid_at():
    inv = _make_invoice()
    inv.pull_domain_events()  # clear create event
    inv.mark_paid()
    assert inv.status is InvoiceStatus.PAID
    assert inv.paid_at is not None


def test_mark_paid_emits_invoice_paid():
    inv = _make_invoice()
    inv.pull_domain_events()  # clear create event
    inv.mark_paid()
    events = inv.pull_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], InvoicePaid)


def test_mark_paid_already_paid_raises_error():
    inv = _make_invoice()
    inv.mark_paid()
    with pytest.raises(InvoiceAlreadyPaidError):
        inv.mark_paid()
