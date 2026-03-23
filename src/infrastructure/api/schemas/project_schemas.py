from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=500)
    org_id: str


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    org_id: str
    tenant_id: str
    status: str
    created_at: str
