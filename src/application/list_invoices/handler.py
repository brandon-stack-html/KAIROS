from src.application.list_invoices.command import ListInvoicesCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.invoice.invoice import Invoice
from src.domain.organization.errors import OrganizationNotFoundError
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId


class ListInvoicesHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListInvoicesCommand) -> list[Invoice]:
        async with self._uow:
            org_id = OrganizationId.from_str(command.org_id)
            tenant_id = TenantId.from_str(command.tenant_id)
            org = await self._uow.organizations.find_by_id(org_id, tenant_id)
            if org is None:
                raise OrganizationNotFoundError(command.org_id)
            return await self._uow.invoices.find_by_org(org_id, tenant_id)
