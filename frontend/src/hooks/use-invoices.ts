import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { invoicesApi } from "@/lib/api/invoices.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import { CreateInvoiceDto } from "@/types/invoice.types";

export function useInvoices(orgId: string) {
  return useQuery({
    queryKey: queryKeys.invoices.byOrg(orgId),
    queryFn: () => invoicesApi.listByOrg(orgId).then((res) => res.data),
    enabled: !!orgId,
  });
}

export function useCreateInvoice(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateInvoiceDto) =>
      invoicesApi.create(orgId, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.invoices.byOrg(orgId),
      });
      toast.success("Factura creada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useMarkInvoicePaid(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      invoicesApi.markPaid(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.invoices.byOrg(orgId),
      });
      toast.success("Factura marcada como pagada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}
