from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    organizations_count: int
    projects_total: int
    projects_active: int
    projects_completed: int
    deliverables_total: int
    deliverables_pending: int
    deliverables_approved: int
    deliverables_changes_requested: int
    invoices_total_amount: str
    invoices_paid_amount: str
    invoices_pending_amount: str
