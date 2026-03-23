"""Driven ports for the Invoice bounded context."""

from abc import ABC, abstractmethod

from src.domain.invoice.invoice import Invoice
from src.domain.shared.invoice_id import InvoiceId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId


class IInvoiceRepository(ABC):
    @abstractmethod
    async def save(self, invoice: Invoice) -> None: ...

    @abstractmethod
    async def find_by_id(
        self, invoice_id: InvoiceId, tenant_id: TenantId
    ) -> Invoice | None: ...

    @abstractmethod
    async def find_by_org(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> list[Invoice]: ...
