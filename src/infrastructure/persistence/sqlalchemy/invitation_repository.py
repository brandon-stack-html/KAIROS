"""SqlAlchemyInvitationRepository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.organization.invitation import Invitation
from src.domain.organization.repository import IInvitationRepository
from src.domain.shared.invitation_id import InvitationId
from src.domain.shared.organization_id import OrganizationId
from src.domain.user.user import UserEmail
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyInvitationRepository(
    SqlAlchemyRepository[Invitation], IInvitationRepository
):
    _entity_class = Invitation

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def save(self, invitation: Invitation) -> None:
        await self._session.merge(invitation)

    async def find_by_id(self, inv_id: InvitationId) -> Invitation | None:
        result = await self._session.execute(
            select(Invitation).where(Invitation.id == inv_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def find_pending_by_email(
        self, email: UserEmail, org_id: OrganizationId
    ) -> Invitation | None:
        result = await self._session.execute(
            select(Invitation)
            .where(Invitation.invitee_email == email)  # type: ignore[attr-defined]
            .where(
                Invitation.org_id == org_id.value
            )  # org_id stored as str  # type: ignore[attr-defined]
            .where(Invitation.is_accepted.is_(False))  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()
