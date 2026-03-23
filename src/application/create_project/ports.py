"""IProjectUnitOfWork — port for project use cases."""

from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.organization.repository import IOrganizationRepository
from src.domain.project.repository import IProjectRepository


class IProjectUnitOfWork(AbstractUnitOfWork, ABC):
    organizations: IOrganizationRepository
    projects: IProjectRepository
