from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(
        min_length=2,
        max_length=63,
        pattern=r"^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$",
        description="Lowercase alphanumeric slug, hyphens allowed (DNS-safe).",
    )


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
