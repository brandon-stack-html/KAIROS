from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.deliverable.repository import IDeliverableRepository
from src.domain.project.repository import IProjectRepository


class IGenerateClientUpdateUnitOfWork(AbstractUnitOfWork, ABC):
    projects: IProjectRepository
    deliverables: IDeliverableRepository
