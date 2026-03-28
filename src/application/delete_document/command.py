from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteDocumentCommand:
    document_id: str
    requester_id: str
    tenant_id: str
