from src.domain.shared.errors import DomainError, EntityNotFoundError


class InvoiceNotFoundError(EntityNotFoundError):
    def __init__(self, invoice_id: str) -> None:
        super().__init__(f"Invoice '{invoice_id}' not found.")


class InvoiceAlreadyPaidError(DomainError):
    def __init__(self) -> None:
        super().__init__("Invoice has already been paid.")


class InvalidInvoiceAmountError(DomainError):
    def __init__(self, amount: object) -> None:
        super().__init__(
            f"Invalid invoice amount: {amount!r}. Must be a positive number."
        )


class InvalidInvoiceTitleError(DomainError):
    def __init__(self, title: str) -> None:
        super().__init__(f"Invalid invoice title: {title!r}. Must be 2–100 characters.")
