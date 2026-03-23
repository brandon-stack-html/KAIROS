from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitDeliverableCommand:
    title: str
    url_link: str
    project_id: str
    submitter_id: str
    tenant_id: str
