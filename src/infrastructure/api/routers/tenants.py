"""Tenants router — public endpoints for tenant lookup and creation."""

from fastapi import APIRouter, Depends, Request, status

from src.application.create_tenant.command import CreateTenantCommand
from src.application.create_tenant.handler import CreateTenantHandler
from src.application.get_tenant_by_slug.command import GetTenantBySlugCommand
from src.application.get_tenant_by_slug.handler import GetTenantBySlugHandler
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.tenant_schemas import TenantCreate, TenantResponse
from src.infrastructure.config.container import (
    get_create_tenant_handler,
    get_get_tenant_by_slug_handler,
)

router = APIRouter(prefix="/tenants", tags=["tenants"])


def _tenant_response(tenant) -> TenantResponse:
    return TenantResponse(
        id=tenant.id.value,
        name=tenant.name,
        slug=tenant.slug,
    )


@router.get(
    "/by-slug/{slug}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    summary="Look up a tenant by slug",
)
@limiter.limit("20/minute")
async def get_tenant_by_slug(
    slug: str,
    request: Request,
    handler: GetTenantBySlugHandler = Depends(get_get_tenant_by_slug_handler),
) -> TenantResponse:
    tenant = await handler.handle(GetTenantBySlugCommand(slug=slug))
    return _tenant_response(tenant)


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant",
)
@limiter.limit("5/minute")
async def create_tenant(
    request: Request,
    body: TenantCreate,
    handler: CreateTenantHandler = Depends(get_create_tenant_handler),
) -> TenantResponse:
    tenant = await handler.handle(CreateTenantCommand(name=body.name, slug=body.slug))
    return _tenant_response(tenant)
