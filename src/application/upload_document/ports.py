from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.document.repository import IDocumentRepository


class IDocumentUnitOfWork(AbstractUnitOfWork, ABC):
    documents: IDocumentRepository
