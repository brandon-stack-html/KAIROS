from dataclasses import dataclass


@dataclass(frozen=True)
class UploadDocumentCommand:
    org_id: str
    project_id: str | None
    uploaded_by: str
    filename: str
    file_type: str
    file_content: bytes
