from src.application.create_organization.command import CreateOrganizationCommand
from src.application.create_organization.ports import IOrganizationUnitOfWork
from src.domain.organization.organization import Organization
from src.domain.shared.errors import ConflictError
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class CreateOrganizationHandler:
    def __init__(self, uow: IOrganizationUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: CreateOrganizationCommand) -> Organization:
        """Returns the created Organization (with memberships populated)."""
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)

            if await self._uow.organizations.exists_by_slug(command.slug, tenant_id):
                raise ConflictError(
                    f"An organization with slug '{command.slug}' already exists in this tenant."
                )

            org = Organization.create(
                name=command.name,
                slug=command.slug,
                owner_id=UserId(command.owner_id),
                tenant_id=tenant_id,
            )

            await self._uow.organizations.save(org)

        return org
