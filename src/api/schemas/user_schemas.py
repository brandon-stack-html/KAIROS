"""Pydantic v2 schemas for the /users endpoint.

Validation lives here, NOT in the domain. The domain only
receives already-parsed data via the application command.
"""
from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
