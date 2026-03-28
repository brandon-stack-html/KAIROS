from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    org_id: str
    project_id: str | None
    uploaded_by: str
    filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    created_at: str
