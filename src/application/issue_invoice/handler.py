from decimal import Decimal, InvalidOperation

from src.application.issue_invoice.command import IssueInvoiceCommand
from src.application.issue_invoice.ports import IInvoiceUnitOfWork
from src.domain.invoice.errors import InvalidInvoiceAmountError
from src.domain.invoice.invoice import Invoice
from src.domain.organization.errors import (
    InsufficientRoleError,
    OrganizationNotFoundError,
)
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class IssueInvoiceHandler:
    def __init__(self, uow: IInvoiceUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: IssueInvoiceCommand) -> Invoice:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            org_id = OrganizationId.from_str(command.org_id)
            issuer_id = UserId(command.issuer_id)

            org = await self._uow.organizations.find_by_id(org_id, tenant_id)
            if org is None:
                raise OrganizationNotFoundError(command.org_id)

            membership = org._find_membership(issuer_id)
            if membership is None or membership.role not in (Role.OWNER, Role.ADMIN):
                raise InsufficientRoleError(
                    "Only an OWNER or ADMIN can issue invoices."
                )

            try:
                amount = Decimal(command.amount)
            except InvalidOperation as exc:
                raise InvalidInvoiceAmountError(command.amount) from exc

            invoice = Invoice.create(
                title=command.title,
                amount=amount,
                org_id=org_id,
                tenant_id=tenant_id,
                issued_by=command.issuer_id,
            )
            await self._uow.invoices.save(invoice)

        return invoice
