from pydantic import BaseModel, Field


class DeliverableCreate(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    url_link: str = Field(min_length=1, max_length=2048)


class DeliverableResponse(BaseModel):
    id: str
    title: str
    url_link: str
    project_id: str
    tenant_id: str
    status: str
    created_at: str
    updated_at: str


class AiFeedbackRequest(BaseModel):
    feedback_text: str = Field(min_length=1, max_length=2000)


class AiFeedbackResponse(BaseModel):
    deliverable_id: str
    feedback_text: str
    ai_structured_feedback: str
