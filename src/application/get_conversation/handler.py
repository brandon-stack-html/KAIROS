from src.application.create_conversation.ports import IConversationUnitOfWork
from src.application.get_conversation.command import GetConversationCommand
from src.domain.conversation.conversation import Conversation
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.shared.conversation_id import ConversationId


class GetConversationHandler:
    def __init__(self, uow: IConversationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: GetConversationCommand) -> Conversation:
        async with self._uow:
            conversation = await self._uow.conversations.find_by_id(
                ConversationId.from_str(command.conversation_id)
            )
            if conversation is None:
                raise ConversationNotFoundError(command.conversation_id)

        return conversation
