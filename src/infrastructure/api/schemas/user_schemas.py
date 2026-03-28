"""Pydantic v2 schemas for user-related endpoints.

Validation lives here, NOT in the domain. The domain only
receives already-parsed data via the application command.
"""

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    tenant_id: str = Field(
        description="UUID v4 of the tenant this user belongs to.",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    )


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    is_active: bool


class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=2048)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(
        description="UUID v4 refresh token issued at login or last refresh.",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    )


class LogoutRequest(BaseModel):
    refresh_token: str = Field(
        description="The refresh token to invalidate.",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    )
