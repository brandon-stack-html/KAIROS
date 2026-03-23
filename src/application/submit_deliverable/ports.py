"""IDeliverableUnitOfWork — port for deliverable use cases."""

from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.deliverable.repository import IDeliverableRepository
from src.domain.organization.repository import IOrganizationRepository
from src.domain.project.repository import IProjectRepository


class IDeliverableUnitOfWork(AbstractUnitOfWork, ABC):
    projects: IProjectRepository
    deliverables: IDeliverableRepository
    organizations: IOrganizationRepository
