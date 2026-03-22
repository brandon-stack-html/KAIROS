"""ITenantRepository — driven port for tenant persistence."""
from abc import ABC, abstractmethod

from src.domain.shared.tenant_id import TenantId


class ITenantRepository(ABC):
    @abstractmethod
    async def save(self, tenant: "Tenant") -> None:  # type: ignore[name-defined]  # noqa: F821
        ...

    @abstractmethod
    async def find_by_id(self, tenant_id: TenantId) -> "Tenant | None":  # type: ignore[name-defined]  # noqa: F821
        ...

    @abstractmethod
    async def find_by_slug(self, slug: str) -> "Tenant | None":  # type: ignore[name-defined]  # noqa: F821
        ...

    @abstractmethod
    async def exists_by_slug(self, slug: str) -> bool:
        ...
