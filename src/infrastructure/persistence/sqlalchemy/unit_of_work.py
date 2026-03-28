from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.register_user.ports import IUserUnitOfWork
from src.infrastructure.persistence.sqlalchemy.conversation_repository import (
    SqlAlchemyConversationRepository,
)
from src.infrastructure.persistence.sqlalchemy.deliverable_repository import (
    SqlAlchemyDeliverableRepository,
)
from src.infrastructure.persistence.sqlalchemy.invitation_repository import (
    SqlAlchemyInvitationRepository,
)
from src.infrastructure.persistence.sqlalchemy.invoice_repository import (
    SqlAlchemyInvoiceRepository,
)
from src.infrastructure.persistence.sqlalchemy.message_repository import (
    SqlAlchemyMessageRepository,
)
from src.infrastructure.persistence.sqlalchemy.organization_repository import (
    SqlAlchemyOrganizationRepository,
)
from src.infrastructure.persistence.sqlalchemy.project_repository import (
    SqlAlchemyProjectRepository,
)
from src.infrastructure.persistence.sqlalchemy.refresh_token_repository import (
    SqlAlchemyRefreshTokenStore,
)
from src.infrastructure.persistence.sqlalchemy.tenant_context import set_tenant
from src.infrastructure.persistence.sqlalchemy.tenant_repository import (
    SqlAlchemyTenantRepository,
)
from src.infrastructure.persistence.sqlalchemy.user_repository import (
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(IUserUnitOfWork):
    """Manages a single AsyncSession per unit of work.

    tenant_id — when provided:
      1. Repositories filter all queries by this tenant_id (application-level isolation).
      2. set_tenant() binds the value to the DB session for PostgreSQL RLS policies.

    Usage:
        async with uow:
            user = await uow.users.find_by_email(email)
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        tenant_id: str | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._tenant_id = tenant_id

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session: AsyncSession = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session, tenant_id=self._tenant_id)
        self.tenants = SqlAlchemyTenantRepository(self._session)
        self.refresh_tokens = SqlAlchemyRefreshTokenStore(self._session)
        self.organizations = SqlAlchemyOrganizationRepository(
            self._session, tenant_id=self._tenant_id
        )
        self.invitations = SqlAlchemyInvitationRepository(self._session)
        self.projects = SqlAlchemyProjectRepository(
            self._session, tenant_id=self._tenant_id
        )
        self.deliverables = SqlAlchemyDeliverableRepository(
            self._session, tenant_id=self._tenant_id
        )
        self.invoices = SqlAlchemyInvoiceRepository(
            self._session, tenant_id=self._tenant_id
        )
        self.conversations = SqlAlchemyConversationRepository(self._session)
        self.messages = SqlAlchemyMessageRepository(self._session)
        if self._tenant_id:
            await set_tenant(self._session, self._tenant_id)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
