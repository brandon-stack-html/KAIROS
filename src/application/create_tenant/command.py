from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTenantCommand:
    name: str
    slug: str
