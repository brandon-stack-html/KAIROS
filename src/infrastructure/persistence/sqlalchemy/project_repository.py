"""SqlAlchemyProjectRepository — tenant-scoped project queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.project.project import Project
from src.domain.project.repository import IProjectRepository
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.project_id import ProjectId
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId
from src.infrastructure.persistence.sqlalchemy.tables.memberships_table import (
    memberships_table,
)
from src.infrastructure.shared.persistence.sqlalchemy_repository import (
    SqlAlchemyRepository,
)


class SqlAlchemyProjectRepository(SqlAlchemyRepository[Project], IProjectRepository):
    _entity_class = Project

    def __init__(self, session: AsyncSession, tenant_id: str | None = None) -> None:
        super().__init__(session)
        self._tenant_id = tenant_id

    async def save(self, project: Project) -> None:
        """Upsert the project aggregate."""
        await self._session.merge(project)

    async def find_by_id(
        self, project_id: ProjectId, tenant_id: TenantId
    ) -> Project | None:
        stmt = (
            select(Project)
            .where(Project.id == project_id)  # type: ignore[attr-defined]
            .where(Project.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_org(
        self, org_id: OrganizationId, tenant_id: TenantId
    ) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.org_id == org_id)  # type: ignore[attr-defined]
            .where(Project.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_user_orgs(
        self, user_id: UserId, tenant_id: TenantId
    ) -> list[Project]:
        """Return all projects belonging to orgs the user is a member of."""
        stmt = (
            select(Project)
            .join(
                memberships_table,
                Project.org_id == memberships_table.c.org_id,  # type: ignore[attr-defined]
            )
            .where(memberships_table.c.user_id == user_id)
            .where(Project.tenant_id == tenant_id)  # type: ignore[attr-defined]
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().unique().all())
