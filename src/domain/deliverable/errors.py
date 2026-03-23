from src.domain.shared.errors import DomainError, EntityNotFoundError


class DeliverableNotFoundError(EntityNotFoundError):
    def __init__(self, deliverable_id: str) -> None:
        super().__init__(f"Deliverable '{deliverable_id}' not found.")


class DeliverableAlreadyReviewedError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Deliverable has already been reviewed (approved or changes requested)."
        )


class InvalidDeliverableTitleError(DomainError):
    def __init__(self, title: str) -> None:
        super().__init__(
            f"Invalid deliverable title: {title!r}. Must be 2–100 characters."
        )


class InvalidDeliverableUrlError(DomainError):
    def __init__(self) -> None:
        super().__init__("Deliverable URL link cannot be empty.")
