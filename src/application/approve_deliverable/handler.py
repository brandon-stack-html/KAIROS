from src.application.approve_deliverable.command import ApproveDeliverableCommand
from src.application.submit_deliverable.ports import IDeliverableUnitOfWork
from src.domain.deliverable.deliverable import Deliverable
from src.domain.deliverable.errors import DeliverableNotFoundError
from src.domain.organization.errors import (
    InsufficientRoleError,
    OrganizationNotFoundError,
)
from src.domain.shared.deliverable_id import DeliverableId
from src.domain.shared.organization_id import OrganizationId
from src.domain.shared.role import Role
from src.domain.shared.tenant_id import TenantId
from src.domain.user.user import UserId


class ApproveDeliverableHandler:
    def __init__(self, uow: IDeliverableUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, command: ApproveDeliverableCommand) -> Deliverable:
        async with self._uow:
            tenant_id = TenantId.from_str(command.tenant_id)
            deliverable_id = DeliverableId.from_str(command.deliverable_id)
            approver_id = UserId(command.approver_id)

            deliverable = await self._uow.deliverables.find_by_id(
                deliverable_id, tenant_id
            )
            if deliverable is None:
                raise DeliverableNotFoundError(command.deliverable_id)

            project = await self._uow.projects.find_by_id(
                deliverable.project_id, tenant_id
            )
            if project is None:
                raise OrganizationNotFoundError(deliverable.project_id.value)

            org = await self._uow.organizations.find_by_id(
                OrganizationId.from_str(project.org_id.value), tenant_id
            )
            if org is None:
                raise OrganizationNotFoundError(project.org_id.value)

            membership = org._find_membership(approver_id)
            if membership is None or membership.role not in (Role.OWNER, Role.ADMIN):
                raise InsufficientRoleError(
                    "Only an OWNER or ADMIN can approve deliverables."
                )

            deliverable.approve(command.approver_id)
            await self._uow.deliverables.save(deliverable)

        return deliverable
