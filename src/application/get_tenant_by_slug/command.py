from dataclasses import dataclass


@dataclass(frozen=True)
class GetTenantBySlugCommand:
    slug: str
