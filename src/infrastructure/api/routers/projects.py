"""Projects router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, Query, Request, status

from src.application.create_project.command import CreateProjectCommand
from src.application.create_project.handler import CreateProjectHandler
from src.application.generate_client_update.command import GenerateClientUpdateCommand
from src.application.generate_client_update.handler import GenerateClientUpdateHandler
from src.application.get_project.command import GetProjectCommand
from src.application.get_project.handler import GetProjectHandler
from src.application.list_deliverables.command import ListDeliverablesCommand
from src.application.list_deliverables.handler import ListDeliverablesHandler
from src.application.list_projects.command import ListProjectsCommand
from src.application.list_projects.handler import ListProjectsHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.deliverable_schemas import DeliverableResponse
from src.infrastructure.api.schemas.project_schemas import (
    ProjectCreate,
    ProjectResponse,
)
from src.infrastructure.config.container import (
    get_create_project_handler,
    get_generate_client_update_handler,
    get_get_project_handler,
    get_list_deliverables_handler,
    get_list_projects_handler,
)

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_response(project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id.value,
        name=project.name,
        description=project.description,
        org_id=project.org_id.value,
        tenant_id=project.tenant_id.value,
        status=project.status.value,
        created_at=project.created_at.isoformat(),
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
@limiter.limit("30/minute")
async def create_project(
    request: Request,
    body: ProjectCreate,
    payload: dict = Depends(get_current_user),
    handler: CreateProjectHandler = Depends(get_create_project_handler),
) -> ProjectResponse:
    tenant_id: str = request.state.tenant_id
    owner_id: str = payload["sub"]
    project = await handler.handle(
        CreateProjectCommand(
            name=body.name,
            description=body.description,
            org_id=body.org_id,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )
    return _project_response(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="List projects",
)
@limiter.limit("60/minute")
async def list_projects(
    request: Request,
    org_id: str | None = Query(default=None),
    payload: dict = Depends(get_current_user),
    handler: ListProjectsHandler = Depends(get_list_projects_handler),
) -> list[ProjectResponse]:
    tenant_id: str = request.state.tenant_id
    user_id: str = payload["sub"]
    projects = await handler.handle(
        ListProjectsCommand(
            user_id=user_id,
            tenant_id=tenant_id,
            org_id=org_id,
        )
    )
    return [_project_response(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
)
@limiter.limit("60/minute")
async def get_project(
    project_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GetProjectHandler = Depends(get_get_project_handler),
) -> ProjectResponse:
    tenant_id: str = request.state.tenant_id
    project = await handler.handle(
        GetProjectCommand(project_id=project_id, tenant_id=tenant_id)
    )
    return _project_response(project)


@router.get(
    "/{project_id}/deliverables",
    response_model=list[DeliverableResponse],
    status_code=status.HTTP_200_OK,
    summary="List deliverables for a project",
)
@limiter.limit("60/minute")
async def list_deliverables(
    project_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListDeliverablesHandler = Depends(get_list_deliverables_handler),
) -> list[DeliverableResponse]:
    tenant_id: str = request.state.tenant_id
    deliverables = await handler.handle(
        ListDeliverablesCommand(project_id=project_id, tenant_id=tenant_id)
    )
    return [
        DeliverableResponse(
            id=d.id.value,
            title=d.title,
            url_link=d.url_link,
            project_id=d.project_id.value,
            tenant_id=d.tenant_id.value,
            status=d.status.value,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat(),
        )
        for d in deliverables
    ]


@router.get(
    "/{project_id}/summary",
    status_code=status.HTTP_200_OK,
    summary="Generate an AI executive summary for a project",
)
@limiter.limit("10/minute")
async def get_project_summary(
    project_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GenerateClientUpdateHandler = Depends(get_generate_client_update_handler),
) -> dict[str, str]:
    tenant_id: str = request.state.tenant_id
    summary = await handler.handle(
        GenerateClientUpdateCommand(
            project_id=project_id,
            tenant_id=tenant_id,
        )
    )
    return {"summary": summary}
