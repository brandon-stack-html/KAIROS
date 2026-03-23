"""Invoices router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, Request, status

from src.application.issue_invoice.command import IssueInvoiceCommand
from src.application.issue_invoice.handler import IssueInvoiceHandler
from src.application.mark_invoice_paid.command import MarkInvoicePaidCommand
from src.application.mark_invoice_paid.handler import MarkInvoicePaidHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.invoice_schemas import (
    InvoiceCreate,
    InvoiceResponse,
)
from src.infrastructure.config.container import (
    get_issue_invoice_handler,
    get_mark_invoice_paid_handler,
)

router = APIRouter(tags=["invoices"])


def _invoice_response(invoice) -> InvoiceResponse:
    return InvoiceResponse(
        id=invoice.id.value,
        title=invoice.title,
        amount=str(
            invoice.amount
        ),  # CRITICAL: Decimal → str to avoid float precision loss
        org_id=invoice.org_id.value,
        tenant_id=invoice.tenant_id.value,
        status=invoice.status.value,
        created_at=invoice.created_at.isoformat(),
        paid_at=invoice.paid_at.isoformat() if invoice.paid_at else None,
    )


@router.post(
    "/organizations/{org_id}/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Issue a new invoice for an organization",
)
@limiter.limit("30/minute")
async def issue_invoice(
    org_id: str,
    request: Request,
    body: InvoiceCreate,
    payload: dict = Depends(get_current_user),
    handler: IssueInvoiceHandler = Depends(get_issue_invoice_handler),
) -> InvoiceResponse:
    tenant_id: str = request.state.tenant_id
    issuer_id: str = payload["sub"]
    invoice = await handler.handle(
        IssueInvoiceCommand(
            title=body.title,
            amount=body.amount,
            org_id=org_id,
            issuer_id=issuer_id,
            tenant_id=tenant_id,
        )
    )
    return _invoice_response(invoice)


@router.patch(
    "/invoices/{invoice_id}/paid",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark an invoice as paid",
)
@limiter.limit("30/minute")
async def mark_invoice_paid(
    invoice_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: MarkInvoicePaidHandler = Depends(get_mark_invoice_paid_handler),
) -> InvoiceResponse:
    tenant_id: str = request.state.tenant_id
    requester_id: str = payload["sub"]
    invoice = await handler.handle(
        MarkInvoicePaidCommand(
            invoice_id=invoice_id,
            requester_id=requester_id,
            tenant_id=tenant_id,
        )
    )
    return _invoice_response(invoice)
