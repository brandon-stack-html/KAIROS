import api from "./axios-instance";
import type { DashboardStats } from "@/types/dashboard.types";

export const dashboardApi = {
  getStats: () =>
    api.get<DashboardStats>("/dashboard/stats").then((r) => r.data),
};
