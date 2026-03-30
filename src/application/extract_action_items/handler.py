"""ExtractActionItemsHandler — extracts action items from conversation messages."""

from src.application.extract_action_items.command import ExtractActionItemsCommand
from src.application.send_message.ports import IMessagingUnitOfWork
from src.application.shared.ai_service import IAiSummaryService
from src.domain.conversation.conversation import Conversation
from src.domain.conversation.errors import ConversationNotFoundError
from src.domain.message.message import Message
from src.domain.shared.conversation_id import ConversationId


def _build_action_items_prompt(
    conversation: Conversation, messages: list[Message]
) -> str:
    """Build a prompt for AI to extract action items from messages.

    Args:
        conversation: The conversation being analyzed
        messages: List of messages to analyze

    Returns:
        A prompt string for the AI model
    """
    # Format messages in reverse chronological order (most recent first) for readability
    messages_text = "\n".join(
        [
            f"[{m.sender_id.value[:8]}] ({m.created_at.isoformat()}): {m.content}"
            for m in reversed(messages)
        ]
    )

    return f"""You are a project management assistant analyzing a team conversation to extract action items.

Conversation type: {conversation.type.value}
Messages (most recent first):
{messages_text}

Extract action items from this conversation. Return JSON with EXACTLY this structure (no additional fields):
{{
  "action_items": [
    {{
      "task": "clear description of what needs to be done",
      "assigned_to": "sender_id prefix (8 chars) or 'unassigned'",
      "deadline": "mentioned deadline or 'not specified'",
      "priority": "high" | "medium" | "low",
      "source_quote": "the exact message fragment that implies this task"
    }}
  ],
  "summary": "one-sentence summary of the conversation's key decisions"
}}

Rules:
- Only extract ACTIONABLE items — ignore greetings, acknowledgments, questions without commitments
- If someone says "I'll do X" or "can you do Y", that's an action item
- If a deadline is mentioned ("by Friday", "next week"), include it
- assigned_to should be the sender_id prefix (first 8 chars) of the person who should act, or "unassigned"
- Keep tasks specific and concise
- Return ONLY the JSON, no markdown fences, no preamble, no explanation"""


class ExtractActionItemsHandler:
    """Extract action items from a conversation using AI analysis."""

    def __init__(
        self, uow: IMessagingUnitOfWork, ai_service: IAiSummaryService
    ) -> None:
        self._uow = uow
        self._ai = ai_service

    async def handle(self, command: ExtractActionItemsCommand) -> str:
        """Extract action items from a conversation.

        Args:
            command: The action items extraction command

        Returns:
            JSON string with extracted action items and summary

        Raises:
            ConversationNotFoundError: If the conversation does not exist
        """
        # Load conversation and messages inside UoW
        async with self._uow:
            conversation_id = ConversationId.from_str(command.conversation_id)

            conversation = await self._uow.conversations.find_by_id(conversation_id)
            if conversation is None:
                raise ConversationNotFoundError(command.conversation_id)

            # Load messages with pagination
            messages = await self._uow.messages.find_by_conversation(
                conversation_id, page=1, limit=50
            )

        # UoW closed — AI call outside transaction
        # If no messages, return empty result without calling AI
        if not messages:
            return '{"action_items": [], "summary": "No messages in conversation."}'

        prompt = _build_action_items_prompt(conversation, messages)
        ai_response = await self._ai.generate(prompt)

        return ai_response
