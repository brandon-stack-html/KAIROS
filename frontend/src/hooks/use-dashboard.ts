import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "@/lib/api/dashboard.api";
import { queryKeys } from "@/constants/query-keys";

export function useDashboardStats() {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: () => dashboardApi.getStats(),
  });
}
