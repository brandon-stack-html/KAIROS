"""IOrganizationUnitOfWork — port for organization use cases."""

from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.organization.repository import (
    IInvitationRepository,
    IOrganizationRepository,
)


class IOrganizationUnitOfWork(AbstractUnitOfWork, ABC):
    organizations: IOrganizationRepository
    invitations: IInvitationRepository
