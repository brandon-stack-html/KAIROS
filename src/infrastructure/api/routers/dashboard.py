"""Dashboard router."""

from fastapi import APIRouter, Depends, Request

from src.application.get_dashboard_stats.command import GetDashboardStatsCommand
from src.application.get_dashboard_stats.handler import GetDashboardStatsHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.dashboard_schemas import DashboardStatsResponse
from src.infrastructure.config.container import get_dashboard_stats_handler

router = APIRouter(tags=["dashboard"])


@router.get(
    "/dashboard/stats",
    response_model=DashboardStatsResponse,
    summary="Get dashboard statistics for the current user",
)
@limiter.limit("30/minute")
async def get_dashboard_stats(
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GetDashboardStatsHandler = Depends(get_dashboard_stats_handler),
) -> DashboardStatsResponse:
    user_id: str = payload["sub"]
    tenant_id: str = request.state.tenant_id
    stats = await handler.handle(
        GetDashboardStatsCommand(user_id=user_id, tenant_id=tenant_id)
    )
    return DashboardStatsResponse(
        organizations_count=stats.organizations_count,
        projects_total=stats.projects_total,
        projects_active=stats.projects_active,
        projects_completed=stats.projects_completed,
        deliverables_total=stats.deliverables_total,
        deliverables_pending=stats.deliverables_pending,
        deliverables_approved=stats.deliverables_approved,
        deliverables_changes_requested=stats.deliverables_changes_requested,
        invoices_total_amount=str(stats.invoices_total_amount),
        invoices_paid_amount=str(stats.invoices_paid_amount),
        invoices_pending_amount=str(stats.invoices_pending_amount),
    )
