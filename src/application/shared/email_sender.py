"""AbstractEmailSender — application-level email sending port.

EmailMessage is a plain DTO (not a domain entity).
EmailTemplate provides type-safe template identifiers.
build_email() renders templates inline — no external files needed,
keeping the boilerplate self-contained.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


@dataclass
class EmailMessage:
    to: str
    subject: str
    html_body: str
    text_body: str
    from_email: str | None = None


class EmailTemplate(Enum):
    WELCOME = "welcome"
    INVITATION = "invitation"
    PASSWORD_RESET = "password_reset"


# Inline templates — override these in derived projects.
_TEMPLATES: dict[EmailTemplate, dict[str, str]] = {
    EmailTemplate.WELCOME: {
        "subject": "Bienvenido a {app_name}",
        "html": (
            "<p>Hola <strong>{user_name}</strong>,</p>"
            "<p>Bienvenido a <strong>{app_name}</strong>. "
            "Tu cuenta fue creada exitosamente.</p>"
        ),
        "text": (
            "Hola {user_name},\n\n"
            "Bienvenido a {app_name}. Tu cuenta fue creada exitosamente."
        ),
    },
    EmailTemplate.INVITATION: {
        "subject": "Invitación a {org_name}",
        "html": (
            "<p><strong>{inviter_name}</strong> te invita a unirte a "
            "<strong>{org_name}</strong>.</p>"
            '<p><a href="{accept_url}">Aceptar invitación</a></p>'
        ),
        "text": (
            "{inviter_name} te invita a unirte a {org_name}.\n\n"
            "Acepta aquí: {accept_url}"
        ),
    },
    EmailTemplate.PASSWORD_RESET: {
        "subject": "Restablece tu contraseña",
        "html": (
            "<p>Solicitaste restablecer tu contraseña.</p>"
            '<p><a href="{reset_url}">Restablecer contraseña</a></p>'
        ),
        "text": "Solicitud de reset de contraseña: {reset_url}",
    },
}


def build_email(template: EmailTemplate, context: dict) -> EmailMessage:
    """Render an EmailMessage from a template and a context dict.

    The context must include 'to' plus the fields referenced by the template.
    Extra keys in context are silently ignored.
    """
    tmpl = _TEMPLATES[template]
    return EmailMessage(
        to=context["to"],
        subject=tmpl["subject"].format_map(context),
        html_body=tmpl["html"].format_map(context),
        text_body=tmpl["text"].format_map(context),
    )


class AbstractEmailSender(ABC):
    """DRIVEN PORT — implemented by concrete email adapters."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> None: ...
