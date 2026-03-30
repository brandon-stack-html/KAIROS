from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractActionItemsCommand:
    """Extract action items from a conversation using AI.

    Attributes:
        conversation_id: The conversation to analyze
        user_id: The user requesting the extraction
        tenant_id: The tenant context
    """

    conversation_id: str
    user_id: str
    tenant_id: str
