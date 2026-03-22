from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserCommand:
    """Input DTO for the RegisterUser use case.

    Plain-text password arrives here; the handler hashes it before
    passing it to the domain. Validation of format/length is done at
    the API layer (Pydantic schema) before this command is constructed.
    tenant_id: UUID4 string of the tenant this user belongs to.
    """

    email: str
    name: str
    password: str
    tenant_id: str
    app_name: str = "SaaS"  # used in the welcome email subject/body
