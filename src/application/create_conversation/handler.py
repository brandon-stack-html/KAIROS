from src.application.create_conversation.command import CreateConversationCommand
from src.application.create_conversation.ports import IConversationUnitOfWork
from src.domain.conversation.conversation import Conversation
from src.domain.shared.conversation_id import ConversationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId


class CreateConversationHandler:
    def __init__(self, uow: IConversationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateConversationCommand) -> Conversation:
        async with self._uow:
            org_id = OrganizationId.from_str(command.org_id)

            if command.project_id is not None:
                conversation = Conversation.for_project(
                    org_id=org_id,
                    project_id=ProjectId.from_str(command.project_id),
                )
            else:
                conversation = Conversation.for_organization(org_id=org_id)

            await self._uow.conversations.save(conversation)

        return conversation
