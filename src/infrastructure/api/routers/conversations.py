"""Conversations & Messages router — all routes require a valid JWT."""

from fastapi import APIRouter, Depends, Query, Request, status

from src.application.create_conversation.command import CreateConversationCommand
from src.application.create_conversation.handler import CreateConversationHandler
from src.application.delete_message.command import DeleteMessageCommand
from src.application.delete_message.handler import DeleteMessageHandler
from src.application.get_conversation.command import GetConversationCommand
from src.application.get_conversation.handler import GetConversationHandler
from src.application.list_messages.command import ListMessagesCommand
from src.application.list_messages.handler import ListMessagesHandler
from src.application.list_org_conversations.command import ListOrgConversationsCommand
from src.application.list_org_conversations.handler import ListOrgConversationsHandler
from src.application.send_message.command import SendMessageCommand
from src.application.send_message.handler import SendMessageHandler
from src.infrastructure.api.dependencies import get_current_user
from src.infrastructure.api.rate_limiter import limiter
from src.infrastructure.api.schemas.conversation_schemas import (
    ConversationResponse,
    MessageResponse,
    SendMessageRequest,
)
from src.infrastructure.config.container import (
    get_create_conversation_handler,
    get_delete_message_handler,
    get_get_conversation_handler,
    get_list_messages_handler,
    get_list_org_conversations_handler,
    get_send_message_handler,
)

router = APIRouter(tags=["conversations"])


# ── Helpers ───────────────────────────────────────────────────────────


def _conversation_response(c) -> ConversationResponse:
    return ConversationResponse(
        id=c.id.value,
        org_id=c.org_id.value,
        type=c.type.value,
        project_id=c.project_id.value if c.project_id else None,
        created_at=c.created_at.isoformat(),
    )


def _message_response(m) -> MessageResponse:
    return MessageResponse(
        id=m.id.value,
        conversation_id=m.conversation_id.value,
        sender_id=m.sender_id.value,
        content=m.content,
        created_at=m.created_at.isoformat(),
    )


# ── Conversation endpoints ────────────────────────────────────────────


@router.post(
    "/organizations/{org_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an organization conversation",
)
@limiter.limit("30/minute")
async def create_org_conversation(
    org_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: CreateConversationHandler = Depends(get_create_conversation_handler),
) -> ConversationResponse:
    conversation = await handler.handle(
        CreateConversationCommand(org_id=org_id, project_id=None)
    )
    return _conversation_response(conversation)


@router.post(
    "/projects/{project_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a project conversation",
)
@limiter.limit("30/minute")
async def create_project_conversation(
    project_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: CreateConversationHandler = Depends(get_create_conversation_handler),
) -> ConversationResponse:
    # The handler needs org_id — but conversations for a project still
    # belong to an org.  Fetch the project first to get org_id.
    from src.application.get_project.command import GetProjectCommand
    from src.application.get_project.handler import GetProjectHandler
    from src.infrastructure.config.container import get_get_project_handler

    tenant_id: str = request.state.tenant_id
    project_handler: GetProjectHandler = get_get_project_handler()
    project = await project_handler.handle(
        GetProjectCommand(project_id=project_id, tenant_id=tenant_id)
    )

    conversation = await handler.handle(
        CreateConversationCommand(
            org_id=project.org_id.value,
            project_id=project_id,
        )
    )
    return _conversation_response(conversation)


@router.get(
    "/organizations/{org_id}/conversations",
    response_model=list[ConversationResponse],
    status_code=status.HTTP_200_OK,
    summary="List conversations for an organization",
)
@limiter.limit("60/minute")
async def list_org_conversations(
    org_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: ListOrgConversationsHandler = Depends(get_list_org_conversations_handler),
) -> list[ConversationResponse]:
    conversations = await handler.handle(ListOrgConversationsCommand(org_id=org_id))
    return [_conversation_response(c) for c in conversations]


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation details",
)
@limiter.limit("60/minute")
async def get_conversation(
    conversation_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: GetConversationHandler = Depends(get_get_conversation_handler),
) -> ConversationResponse:
    conversation = await handler.handle(
        GetConversationCommand(conversation_id=conversation_id)
    )
    return _conversation_response(conversation)


# ── Message endpoints ─────────────────────────────────────────────────


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a conversation",
)
@limiter.limit("30/minute")
async def send_message(
    conversation_id: str,
    body: SendMessageRequest,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: SendMessageHandler = Depends(get_send_message_handler),
) -> MessageResponse:
    sender_id: str = payload["sub"]
    message = await handler.handle(
        SendMessageCommand(
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=body.content,
        )
    )
    return _message_response(message)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="List messages in a conversation",
)
@limiter.limit("60/minute")
async def list_messages(
    conversation_id: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    handler: ListMessagesHandler = Depends(get_list_messages_handler),
) -> list[MessageResponse]:
    messages = await handler.handle(
        ListMessagesCommand(
            conversation_id=conversation_id,
            page=page,
            limit=limit,
        )
    )
    return [_message_response(m) for m in messages]


@router.delete(
    "/messages/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a message (sender only)",
)
@limiter.limit("30/minute")
async def delete_message(
    message_id: str,
    request: Request,
    payload: dict = Depends(get_current_user),
    handler: DeleteMessageHandler = Depends(get_delete_message_handler),
) -> None:
    requester_id: str = payload["sub"]
    await handler.handle(
        DeleteMessageCommand(
            message_id=message_id,
            requester_id=requester_id,
        )
    )
