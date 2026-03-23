from src.application.issue_invoice.ports import IInvoiceUnitOfWork
from src.application.mark_invoice_paid.command import MarkInvoicePaidCommand
from src.domain.invoice.errors import InvoiceNotFoundError
from src.domain.invoice.invoice import Invoice
from src.domain.organization.errors import (
    InsufficientRoleError,
    OrganizationNotFoundError,
)
from src.domain.shared.invoice_id import InvoiceId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class MarkInvoicePaidHandler:
    def __init__(self, uow: IInvoiceUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: MarkInvoicePaidCommand) -> Invoice:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            invoice_id = InvoiceId.from_str(command.invoice_id)
            requester_id = UserId(command.requester_id)

            invoice = await self._uow.invoices.find_by_id(invoice_id, tenant_id)
            if invoice is None:
                raise InvoiceNotFoundError(command.invoice_id)

            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(invoice.org_id.value), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(invoice.org_id.value)

            membership = org._find_membership(requester_id)
            if membership is None or membership.role not in (Role.OWNER, Role.ADMIN):
                raise InsufficientRoleError(
                    "Only an OWNER or ADMIN can mark invoices as paid."
                )

            invoice.mark_paid()
            await self._uow.invoices.save(invoice)

        return invoice
