"""SqlAlchemyInvoiceRepository — tenant-scoped invoice queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.invoice.invoice import Invoice
from src.domain.invoice.repository import IInvoiceRepository
from src.domain.shared.invoice_id import InvoiceId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.tenant_id import TenantId
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyInvoiceRepository(SqlAlchemyRepository[Invoice], IInvoiceRepository):
    _entity_class = Invoice

    def __init__(self, session: AsyncSession, tenant_id: str | None = None) -> None:
        super().__init__(session)
        self._tenant_id = tenant_id

    async def save(self, invoice: Invoice) -> None:
        """Upsert the invoice aggregate."""
        await self._session.merge(invoice)

    async def find_by_id(
        self, invoice_id: InvoiceId, tenant_id: TenantId
    ) -> Invoice | None:
        stmt = (
            select(Invoice)
            .where(Invoice.id == invoice_id)  # type: ignore[attr-defined]
            .where(Invoice.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_org(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> list[Invoice]:
        stmt = (
            select(Invoice)
            .where(Invoice.org_id == org_id)  # type: ignore[attr-defined]
            .where(Invoice.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_tenant(self, tenant_id: TenantId) -> list[Invoice]:
        stmt = select(Invoice).where(Invoice.tenant_id == tenant_id)  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
