from dataclasses import dataclass


@dataclass(frozen=True)
class DownloadDocumentCommand:
    document_id: str
