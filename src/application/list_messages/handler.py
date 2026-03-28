from src.application.list_messages.command import ListMessagesCommand
from src.application.send_message.ports import IMessagingUnitOfWork
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId


class ListMessagesHandler:
    def __init__(self, uow: IMessagingUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ListMessagesCommand) -> list[Message]:
        async with self._uow:
            conversation_id = ConversationId.from_str(command.conversation_id)
            conversation = await self._uow.conversations.find_by_id(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError(command.conversation_id)

            return await self._uow.messages.find_by_conversation(
                conversation_id,
                page=command.page,
                limit=command.limit,
            )
