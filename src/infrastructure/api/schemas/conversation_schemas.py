"""Pydantic v2 schemas for conversation and message endpoints."""

from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class ConversationResponse(BaseModel):
    id: str
    org_id: str
    type: str
    project_id: str | None = None
    created_at: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    sender_id: str
    content: str
    created_at: str
