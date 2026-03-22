"""Pydantic v2 schemas for organization endpoints."""
from pydantic import BaseModel, EmailStr, Field

from src.domain.shared.role import Role


class OrgCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(
        min_length=2,
        max_length=63,
        pattern=r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$",
        description="Lowercase alphanumeric slug, hyphens allowed (DNS-safe).",
    )


class MemberResponse(BaseModel):
    user_id: str
    role: str
    joined_at: str


class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    tenant_id: str
    is_active: bool
    members: list[MemberResponse] = []


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Role = Role.MEMBER


class InvitationResponse(BaseModel):
    id: str
    org_id: str
    invitee_email: str
    role: str
    expires_at: str
    is_accepted: bool


class ChangeMemberRoleRequest(BaseModel):
    role: Role
