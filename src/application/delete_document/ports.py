from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.document.repository import IDocumentRepository
from src.domain.organization.repository import IOrganizationRepository


class IDeleteDocumentUnitOfWork(AbstractUnitOfWork, ABC):
    documents: IDocumentRepository
    organizations: IOrganizationRepository
