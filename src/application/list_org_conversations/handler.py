from src.application.create_conversation.ports import IConversationUnitOfWork
from src.application.list_org_conversations.command import ListOrgConversationsCommand
from src.domain.conversation.conversation import Conversation
from src.domain.shared.organization_id import OrganizationId


class ListOrgConversationsHandler:
    def __init__(self, uow: IConversationUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: ListOrgConversationsCommand
    ) -> list[Conversation]:
        async with self._uow:
            return await self._uow.conversations.find_by_org(
                OrganizationId.from_str(command.org_id)
            )
