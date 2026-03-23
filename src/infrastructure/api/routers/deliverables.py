"""Deliverables router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, Request, status

from src.application.approve_deliverable.command import ApproveDeliverableCommand
from src.application.approve_deliverable.handler import ApproveDeliverableHandler
from src.application.request_changes.command import RequestChangesCommand
from src.application.request_changes.handler import RequestChangesHandler
from src.application.submit_deliverable.command import SubmitDeliverableCommand
from src.application.submit_deliverable.handler import SubmitDeliverableHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.deliverable_schemas import (
    DeliverableCreate,
    DeliverableResponse,
)
from src.infrastructure.config.container import (
    get_approve_deliverable_handler,
    get_request_changes_handler,
    get_submit_deliverable_handler,
)

router = APIRouter(tags=["deliverables"])


def _deliverable_response(deliverable) -> DeliverableResponse:
    return DeliverableResponse(
        id=deliverable.id.value,
        title=deliverable.title,
        url_link=deliverable.url_link,
        project_id=deliverable.project_id.value,
        tenant_id=deliverable.tenant_id.value,
        status=deliverable.status.value,
        created_at=deliverable.created_at.isoformat(),
        updated_at=deliverable.updated_at.isoformat(),
    )


@router.post(
    "/projects/{project_id}/deliverables",
    response_model=DeliverableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new deliverable for a project",
)
@limiter.limit("30/minute")
async def submit_deliverable(
    project_id: str,
    request: Request,
    body: DeliverableCreate,
    payload: dict = Depends(get_current_user),
    handler: SubmitDeliverableHandler = Depends(get_submit_deliverable_handler),
) -> DeliverableResponse:
    tenant_id: str = request.state.tenant_id
    submitter_id: str = payload["sub"]
    deliverable = await handler.handle(
        SubmitDeliverableCommand(
            title=body.title,
            url_link=body.url_link,
            project_id=project_id,
            submitter_id=submitter_id,
            tenant_id=tenant_id,
        )
    )
    return _deliverable_response(deliverable)


@router.patch(
    "/deliverables/{deliverable_id}/approve",
    response_model=DeliverableResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve a deliverable",
)
@limiter.limit("30/minute")
async def approve_deliverable(
    deliverable_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ApproveDeliverableHandler = Depends(get_approve_deliverable_handler),
) -> DeliverableResponse:
    tenant_id: str = request.state.tenant_id
    approver_id: str = payload["sub"]
    deliverable = await handler.handle(
        ApproveDeliverableCommand(
            deliverable_id=deliverable_id,
            approver_id=approver_id,
            tenant_id=tenant_id,
        )
    )
    return _deliverable_response(deliverable)


@router.patch(
    "/deliverables/{deliverable_id}/request-changes",
    response_model=DeliverableResponse,
    status_code=status.HTTP_200_OK,
    summary="Request changes on a deliverable",
)
@limiter.limit("30/minute")
async def request_changes(
    deliverable_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: RequestChangesHandler = Depends(get_request_changes_handler),
) -> DeliverableResponse:
    tenant_id: str = request.state.tenant_id
    reviewer_id: str = payload["sub"]
    deliverable = await handler.handle(
        RequestChangesCommand(
            deliverable_id=deliverable_id,
            reviewer_id=reviewer_id,
            tenant_id=tenant_id,
        )
    )
    return _deliverable_response(deliverable)
