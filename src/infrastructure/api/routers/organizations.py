"""Organizations router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, Request, status

from src.application.accept_invitation.command import AcceptInvitationCommand
from src.application.accept_invitation.handler import AcceptInvitationHandler
from src.application.change_member_role.command import ChangeMemberRoleCommand
from src.application.change_member_role.handler import ChangeMemberRoleHandler
from src.application.create_organization.command import CreateOrganizationCommand
from src.application.create_organization.handler import CreateOrganizationHandler
from src.application.get_organization.command import GetOrganizationCommand
from src.application.get_organization.handler import GetOrganizationHandler
from src.application.invite_member.command import InviteMemberCommand
from src.application.invite_member.handler import InviteMemberHandler
from src.application.list_invoices.command import ListInvoicesCommand
from src.application.list_invoices.handler import ListInvoicesHandler
from src.application.list_organizations.command import ListOrganizationsCommand
from src.application.list_organizations.handler import ListOrganizationsHandler
from src.application.remove_member.command import RemoveMemberCommand
from src.application.remove_member.handler import RemoveMemberHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.invoice_schemas import InvoiceResponse
from src.infrastructure.api.schemas.organization_schemas import (
    ChangeMemberRoleRequest,
    InvitationCreate,
    InvitationResponse,
    MemberResponse,
    OrgCreate,
    OrgResponse,
)
from src.infrastructure.config.container import (
    get_accept_invitation_handler,
    get_change_member_role_handler,
    get_create_organization_handler,
    get_get_organization_handler,
    get_invite_member_handler,
    get_list_invoices_handler,
    get_list_organizations_handler,
    get_remove_member_handler,
)
from src.infrastructure.config.settings import settings

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _org_response(org) -> OrgResponse:
    return OrgResponse(
        id=org.id.value,
        name=org.name,
        slug=org.slug,
        tenant_id=org.tenant_id.value,
        is_active=org.is_active,
        members=[
            MemberResponse(
                user_id=m.user_id.value,
                role=m.role.value,
                joined_at=m.joined_at.isoformat(),
            )
            for m in org.memberships
        ],
    )


@router.post(
    "",
    response_model=OrgResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
@limiter.limit("30/minute")
async def create_organization(
    request: Request,
    body: OrgCreate,
    payload: dict = Depends(get_current_user),
    handler: CreateOrganizationHandler = Depends(get_create_organization_handler),
) -> OrgResponse:
    tenant_id: str = request.state.tenant_id
    owner_id: str = payload["sub"]
    org = await handler.handle(
        CreateOrganizationCommand(
            name=body.name,
            slug=body.slug,
            owner_id=owner_id,
            tenant_id=tenant_id,
        )
    )
    return _org_response(org)


@router.get(
    "",
    response_model=list[OrgResponse],
    status_code=status.HTTP_200_OK,
    summary="List organizations the current user belongs to",
)
@limiter.limit("60/minute")
async def list_organizations(
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListOrganizationsHandler = Depends(get_list_organizations_handler),
) -> list[OrgResponse]:
    tenant_id: str = request.state.tenant_id
    user_id: str = payload["sub"]
    orgs = await handler.handle(
        ListOrganizationsCommand(user_id=user_id, tenant_id=tenant_id)
    )
    return [_org_response(org) for org in orgs]


@router.get(
    "/{org_id}",
    response_model=OrgResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization details",
)
@limiter.limit("60/minute")
async def get_organization(
    org_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GetOrganizationHandler = Depends(get_get_organization_handler),
) -> OrgResponse:
    tenant_id: str = request.state.tenant_id
    org = await handler.handle(
        GetOrganizationCommand(org_id=org_id, tenant_id=tenant_id)
    )
    return _org_response(org)


@router.get(
    "/{org_id}/invoices",
    response_model=list[InvoiceResponse],
    status_code=status.HTTP_200_OK,
    summary="List invoices for an organization",
)
@limiter.limit("60/minute")
async def list_invoices(
    org_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListInvoicesHandler = Depends(get_list_invoices_handler),
) -> list[InvoiceResponse]:
    tenant_id: str = request.state.tenant_id
    invoices = await handler.handle(
        ListInvoicesCommand(org_id=org_id, tenant_id=tenant_id)
    )
    return [
        InvoiceResponse(
            id=inv.id.value,
            title=inv.title,
            amount=str(inv.amount),
            org_id=inv.org_id.value,
            tenant_id=inv.tenant_id.value,
            status=inv.status.value,
            created_at=inv.created_at.isoformat(),
            paid_at=inv.paid_at.isoformat() if inv.paid_at else None,
        )
        for inv in invoices
    ]


@router.post(
    "/{org_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a user to the organization",
)
@limiter.limit("30/minute")
async def invite_member(
    org_id: str,
    request: Request,
    body: InvitationCreate,
    payload: dict = Depends(get_current_user),
    handler: InviteMemberHandler = Depends(get_invite_member_handler),
) -> InvitationResponse:
    tenant_id: str = request.state.tenant_id
    inviter_id: str = payload["sub"]
    invitation = await handler.handle(
        InviteMemberCommand(
            org_id=org_id,
            inviter_id=inviter_id,
            invitee_email=str(body.email),
            role=body.role.value,
            tenant_id=tenant_id,
            frontend_url=settings.frontend_url,
        )
    )
    return InvitationResponse(
        id=invitation.id.value,
        org_id=invitation.org_id,
        invitee_email=invitation.invitee_email.value,
        role=invitation.role.value,
        expires_at=invitation.expires_at.isoformat(),
        is_accepted=invitation.is_accepted,
    )


@router.post(
    "/{org_id}/invitations/{inv_id}/accept",
    response_model=OrgResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept an invitation and join the organization",
)
@limiter.limit("30/minute")
async def accept_invitation(
    org_id: str,
    inv_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: AcceptInvitationHandler = Depends(get_accept_invitation_handler),
) -> OrgResponse:
    tenant_id: str = request.state.tenant_id
    user_id: str = payload["sub"]
    org = await handler.handle(
        AcceptInvitationCommand(
            invitation_id=inv_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
    )
    return _org_response(org)


@router.delete(
    "/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from the organization",
)
@limiter.limit("30/minute")
async def remove_member(
    org_id: str,
    user_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: RemoveMemberHandler = Depends(get_remove_member_handler),
) -> None:
    tenant_id: str = request.state.tenant_id
    remover_id: str = payload["sub"]
    await handler.handle(
        RemoveMemberCommand(
            org_id=org_id,
            remover_id=remover_id,
            user_id=user_id,
            tenant_id=tenant_id,
        )
    )


@router.patch(
    "/{org_id}/members/{user_id}/role",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Change a member's role in the organization",
)
@limiter.limit("30/minute")
async def change_member_role(
    org_id: str,
    user_id: str,
    request: Request,
    body: ChangeMemberRoleRequest,
    payload: dict = Depends(get_current_user),
    handler: ChangeMemberRoleHandler = Depends(get_change_member_role_handler),
) -> MemberResponse:
    tenant_id: str = request.state.tenant_id
    changer_id: str = payload["sub"]
    org = await handler.handle(
        ChangeMemberRoleCommand(
            org_id=org_id,
            changer_id=changer_id,
            user_id=user_id,
            new_role=body.role.value,
            tenant_id=tenant_id,
        )
    )
    from src.domain.user.user import UserId

    membership = next(m for m in org.memberships if m.user_id == UserId(user_id))
    return MemberResponse(
        user_id=membership.user_id.value,
        role=membership.role.value,
        joined_at=membership.joined_at.isoformat(),
    )
