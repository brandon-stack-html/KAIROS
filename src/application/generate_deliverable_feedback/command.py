from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateDeliverableFeedbackCommand:
    """Generate AI-structured feedback for a deliverable.

    Attributes:
        deliverable_id: The deliverable to analyze
        feedback_text: Free-text feedback from the reviewer (1-2000 chars)
        reviewer_id: The user providing the feedback
        tenant_id: The tenant context
    """

    deliverable_id: str
    feedback_text: str
    reviewer_id: str
    tenant_id: str
