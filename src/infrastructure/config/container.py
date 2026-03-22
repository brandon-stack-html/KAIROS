"""Composition root — wires concrete adapters to application ports.

All factory functions are plain callables so they work both with
FastAPI's Depends() and in plain unit/integration tests.
"""
from src.application.accept_invitation.handler import AcceptInvitationHandler
from src.application.change_member_role.handler import ChangeMemberRoleHandler
from src.application.create_organization.handler import CreateOrganizationHandler
from src.application.invite_member.handler import InviteMemberHandler
from src.application.list_organizations.handler import ListOrganizationsHandler
from src.application.login_user.handler import LoginUserHandler
from src.application.logout_user.handler import LogoutHandler
from src.application.refresh_token.handler import RefreshTokenHandler
from src.application.register_user.handler import RegisterUserHandler
from src.application.remove_member.handler import RemoveMemberHandler
from src.application.shared.email_sender import AbstractEmailSender
from src.infrastructure.config.settings import settings
from src.infrastructure.external.email.console_email_sender import ConsoleEmailSender
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.security.jwt_handler import JwtTokenGenerator
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

# ── Singletons (stateless, safe to share) ────────────────────────────
_password_hasher = BcryptPasswordHasher()
_token_generator = JwtTokenGenerator()


def _build_email_sender() -> AbstractEmailSender:
    if settings.email_provider == "resend":
        from src.infrastructure.external.email.resend_email_sender import (
            ResendEmailSender,
        )

        return ResendEmailSender(
            api_key=settings.resend_api_key or "",
            default_from=settings.email_from,
        )
    return ConsoleEmailSender()


_email_sender: AbstractEmailSender = _build_email_sender()


# ── Per-request factories ─────────────────────────────────────────────
def get_uow() -> SqlAlchemyUnitOfWork:
    """New UoW (and therefore a new AsyncSession) per request."""
    return SqlAlchemyUnitOfWork(session_factory=SessionLocal)


def get_email_sender() -> AbstractEmailSender:
    """Shared email sender singleton."""
    return _email_sender


def get_register_user_handler() -> RegisterUserHandler:
    return RegisterUserHandler(
        uow=get_uow(),
        password_hasher=_password_hasher,
        email_sender=_email_sender,
    )


def get_login_user_handler() -> LoginUserHandler:
    return LoginUserHandler(
        uow=get_uow(),
        password_hasher=_password_hasher,
        token_generator=_token_generator,
    )


def get_refresh_token_handler() -> RefreshTokenHandler:
    return RefreshTokenHandler(
        uow=get_uow(),
        token_generator=_token_generator,
    )


def get_logout_handler() -> LogoutHandler:
    return LogoutHandler(uow=get_uow())


def get_create_organization_handler() -> CreateOrganizationHandler:
    return CreateOrganizationHandler(uow=get_uow())


def get_invite_member_handler() -> InviteMemberHandler:
    return InviteMemberHandler(uow=get_uow(), email_sender=_email_sender)


def get_accept_invitation_handler() -> AcceptInvitationHandler:
    return AcceptInvitationHandler(uow=get_uow())


def get_remove_member_handler() -> RemoveMemberHandler:
    return RemoveMemberHandler(uow=get_uow())


def get_change_member_role_handler() -> ChangeMemberRoleHandler:
    return ChangeMemberRoleHandler(uow=get_uow())


def get_list_organizations_handler() -> ListOrganizationsHandler:
    return ListOrganizationsHandler(uow=get_uow())
