import api from "./axios-instance";
import { Invoice, CreateInvoiceDto } from "@/types/invoice.types";

export const invoicesApi = {
  listByOrg: (orgId: string) =>
    api.get<Invoice[]>(`/organizations/${orgId}/invoices`),

  create: (orgId: string, data: CreateInvoiceDto) =>
    api.post<Invoice>(`/organizations/${orgId}/invoices`, data),

  markPaid: (id: string) => api.patch<Invoice>(`/invoices/${id}/paid`),
};
