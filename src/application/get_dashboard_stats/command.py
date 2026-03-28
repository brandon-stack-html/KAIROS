from dataclasses import dataclass


@dataclass(frozen=True)
class GetDashboardStatsCommand:
    user_id: str
    tenant_id: str
