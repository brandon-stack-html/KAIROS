from abc import ABC

from src.application.shared.unit_of_work import AbstractUnitOfWork
from src.domain.invoice.repository import IInvoiceRepository
from src.domain.organization.repository import IOrganizationRepository


class IInvoiceUnitOfWork(AbstractUnitOfWork, ABC):
    organizations: IOrganizationRepository
    invoices: IInvoiceRepository
