from dataclasses import dataclass
from decimal import Decimal

from src.application.get_dashboard_stats.command import GetDashboardStatsCommand
from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.deliverable.deliverable import DeliverableStatus
from src.domain.invoice.invoice import InvoiceStatus
from src.domain.project.project import ProjectStatus
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


@dataclass(frozen=True)
class DashboardStats:
    organizations_count: int
    projects_total: int
    projects_active: int
    projects_completed: int
    deliverables_total: int
    deliverables_pending: int
    deliverables_approved: int
    deliverables_changes_requested: int
    invoices_total_amount: Decimal
    invoices_paid_amount: Decimal
    invoices_pending_amount: Decimal


class GetDashboardStatsHandler:
    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetDashboardStatsCommand) -> DashboardStats:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            user_id = UserId(command.user_id)

            orgs = await self._uow.organizations.find_by_user(user_id, tenant_id)
            projects = await self._uow.projects.find_by_user_orgs(user_id, tenant_id)
            deliverables = await self._uow.deliverables.find_by_tenant(tenant_id)
            invoices = await self._uow.invoices.find_by_tenant(tenant_id)

        projects_active = sum(1 for p in projects if p.status == ProjectStatus.ACTIVE)
        projects_completed = sum(
            1 for p in projects if p.status == ProjectStatus.COMPLETED
        )

        deliverables_pending = sum(
            1 for d in deliverables if d.status == DeliverableStatus.PENDING
        )
        deliverables_approved = sum(
            1 for d in deliverables if d.status == DeliverableStatus.APPROVED
        )
        deliverables_changes_requested = sum(
            1 for d in deliverables if d.status == DeliverableStatus.CHANGES_REQUESTED
        )

        invoices_total = sum((i.amount for i in invoices), Decimal("0"))
        invoices_paid = sum(
            (i.amount for i in invoices if i.status == InvoiceStatus.PAID),
            Decimal("0"),
        )
        invoices_pending = sum(
            (i.amount for i in invoices if i.status != InvoiceStatus.PAID),
            Decimal("0"),
        )

        return DashboardStats(
            organizations_count=len(orgs),
            projects_total=len(projects),
            projects_active=projects_active,
            projects_completed=projects_completed,
            deliverables_total=len(deliverables),
            deliverables_pending=deliverables_pending,
            deliverables_approved=deliverables_approved,
            deliverables_changes_requested=deliverables_changes_requested,
            invoices_total_amount=invoices_total,
            invoices_paid_amount=invoices_paid,
            invoices_pending_amount=invoices_pending,
        )
