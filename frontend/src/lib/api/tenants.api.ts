import api from "./axios-instance";
import { Tenant, CreateTenantDto } from "@/types/tenant.types";

export const tenantsApi = {
  getBySlug: (slug: string) => api.get<Tenant>(`/tenants/by-slug/${slug}`),

  create: (data: CreateTenantDto) => api.post<Tenant>("/tenants", data),
};
