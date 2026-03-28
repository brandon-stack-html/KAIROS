"""Composition root — wires concrete adapters to application ports.

All factory functions are plain callables so they work both with
FastAPI's Depends() and in plain unit/integration tests.
"""

from src.application.get_dashboard_stats.handler import GetDashboardStatsHandler
from src.application.delete_document.handler import DeleteDocumentHandler
from src.application.download_document.handler import DownloadDocumentHandler
from src.application.list_documents.handler import ListDocumentsHandler
from src.application.upload_document.handler import UploadDocumentHandler
from src.application.accept_invitation.handler import AcceptInvitationHandler
from src.application.create_conversation.handler import CreateConversationHandler
from src.application.delete_message.handler import DeleteMessageHandler
from src.application.get_conversation.handler import GetConversationHandler
from src.application.list_messages.handler import ListMessagesHandler
from src.application.list_org_conversations.handler import ListOrgConversationsHandler
from src.application.send_message.handler import SendMessageHandler
from src.application.approve_deliverable.handler import ApproveDeliverableHandler
from src.application.change_member_role.handler import ChangeMemberRoleHandler
from src.application.create_organization.handler import CreateOrganizationHandler
from src.application.create_project.handler import CreateProjectHandler
from src.application.create_tenant.handler import CreateTenantHandler
from src.application.generate_client_update.handler import GenerateClientUpdateHandler
from src.application.get_current_user.handler import GetCurrentUserHandler
from src.application.get_organization.handler import GetOrganizationHandler
from src.application.get_project.handler import GetProjectHandler
from src.application.get_tenant_by_slug.handler import GetTenantBySlugHandler
from src.application.invite_member.handler import InviteMemberHandler
from src.application.issue_invoice.handler import IssueInvoiceHandler
from src.application.list_deliverables.handler import ListDeliverablesHandler
from src.application.list_invoices.handler import ListInvoicesHandler
from src.application.list_organizations.handler import ListOrganizationsHandler
from src.application.list_projects.handler import ListProjectsHandler
from src.application.login_user.handler import LoginUserHandler
from src.application.logout_user.handler import LogoutHandler
from src.application.mark_invoice_paid.handler import MarkInvoicePaidHandler
from src.application.refresh_token.handler import RefreshTokenHandler
from src.application.register_user.handler import RegisterUserHandler
from src.application.remove_member.handler import RemoveMemberHandler
from src.application.request_changes.handler import RequestChangesHandler
from src.application.shared.ai_service import IAiSummaryService
from src.application.shared.email_sender import AbstractEmailSender
from src.application.submit_deliverable.handler import SubmitDeliverableHandler
from src.application.update_user_profile.handler import UpdateUserProfileHandler
from src.infrastructure.config.settings import settings
from src.infrastructure.external.email.console_email_sender import ConsoleEmailSender
from src.infrastructure.persistence.sqlalchemy.database import SessionLocal
from src.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.security.jwt_handler import JwtTokenGenerator
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.infrastructure.storage.local_file_storage import LocalFileStorage

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


def _build_ai_service() -> IAiSummaryService:
    if settings.openrouter_api_key:
        from src.infrastructure.external.ai.openrouter_ai_service import (
            OpenRouterAiService,
        )

        return OpenRouterAiService(
            api_key=settings.openrouter_api_key,
            model=settings.ai_model,
            frontend_url=settings.frontend_url,
        )
    from src.infrastructure.persistence.in_memory.ai_service import InMemoryAiService

    return InMemoryAiService()


_email_sender: AbstractEmailSender = _build_email_sender()
_ai_service: IAiSummaryService = _build_ai_service()
_file_storage = LocalFileStorage(upload_dir=settings.upload_dir)


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


def get_create_project_handler() -> CreateProjectHandler:
    return CreateProjectHandler(uow=get_uow())


def get_list_projects_handler() -> ListProjectsHandler:
    return ListProjectsHandler(uow=get_uow())


def get_submit_deliverable_handler() -> SubmitDeliverableHandler:
    return SubmitDeliverableHandler(uow=get_uow())


def get_approve_deliverable_handler() -> ApproveDeliverableHandler:
    return ApproveDeliverableHandler(uow=get_uow())


def get_request_changes_handler() -> RequestChangesHandler:
    return RequestChangesHandler(uow=get_uow())


def get_issue_invoice_handler() -> IssueInvoiceHandler:
    return IssueInvoiceHandler(uow=get_uow())


def get_mark_invoice_paid_handler() -> MarkInvoicePaidHandler:
    return MarkInvoicePaidHandler(uow=get_uow())


def get_generate_client_update_handler() -> GenerateClientUpdateHandler:
    return GenerateClientUpdateHandler(uow=get_uow(), ai_service=_ai_service)


def get_get_tenant_by_slug_handler() -> GetTenantBySlugHandler:
    return GetTenantBySlugHandler(uow=get_uow())


def get_create_tenant_handler() -> CreateTenantHandler:
    return CreateTenantHandler(uow=get_uow())


def get_current_user_handler() -> GetCurrentUserHandler:
    return GetCurrentUserHandler(uow=get_uow())


def get_get_organization_handler() -> GetOrganizationHandler:
    return GetOrganizationHandler(uow=get_uow())


def get_get_project_handler() -> GetProjectHandler:
    return GetProjectHandler(uow=get_uow())


def get_list_deliverables_handler() -> ListDeliverablesHandler:
    return ListDeliverablesHandler(uow=get_uow())


def get_list_invoices_handler() -> ListInvoicesHandler:
    return ListInvoicesHandler(uow=get_uow())


def get_update_user_profile_handler() -> UpdateUserProfileHandler:
    return UpdateUserProfileHandler(uow=get_uow())


def get_create_conversation_handler() -> CreateConversationHandler:
    return CreateConversationHandler(uow=get_uow())


def get_get_conversation_handler() -> GetConversationHandler:
    return GetConversationHandler(uow=get_uow())


def get_list_org_conversations_handler() -> ListOrgConversationsHandler:
    return ListOrgConversationsHandler(uow=get_uow())


def get_send_message_handler() -> SendMessageHandler:
    return SendMessageHandler(uow=get_uow())


def get_delete_message_handler() -> DeleteMessageHandler:
    return DeleteMessageHandler(uow=get_uow())


def get_list_messages_handler() -> ListMessagesHandler:
    return ListMessagesHandler(uow=get_uow())


def get_upload_document_handler() -> UploadDocumentHandler:
    return UploadDocumentHandler(uow=get_uow(), file_storage=_file_storage)


def get_list_documents_handler() -> ListDocumentsHandler:
    return ListDocumentsHandler(uow=get_uow())


def get_delete_document_handler() -> DeleteDocumentHandler:
    return DeleteDocumentHandler(uow=get_uow(), file_storage=_file_storage)


def get_download_document_handler() -> DownloadDocumentHandler:
    return DownloadDocumentHandler(uow=get_uow())


def get_dashboard_stats_handler() -> GetDashboardStatsHandler:
    return GetDashboardStatsHandler(uow=get_uow())
