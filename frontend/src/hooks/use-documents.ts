import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi } from "@/lib/api/documents.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";

export function useOrgDocuments(orgId: string) {
  return useQuery({
    queryKey: queryKeys.documents.byOrg(orgId),
    queryFn: () => documentsApi.listByOrg(orgId).then((res) => res.data),
    enabled: !!orgId,
  });
}

export function useProjectDocuments(projectId: string) {
  return useQuery({
    queryKey: queryKeys.documents.byProject(projectId),
    queryFn: () =>
      documentsApi.listByProject(projectId).then((res) => res.data),
    enabled: !!projectId,
  });
}

export function useUploadOrgDocument(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) =>
      documentsApi.uploadToOrg(orgId, file).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.documents.byOrg(orgId),
      });
      toast.success("Documento subido");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useUploadProjectDocument(projectId: string, orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) =>
      documentsApi.uploadToProject(projectId, file).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.documents.byProject(projectId),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.documents.byOrg(orgId),
      });
      toast.success("Documento subido");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useDeleteDocument(orgId?: string, projectId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) => documentsApi.delete(documentId),
    onSuccess: () => {
      if (orgId) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.documents.byOrg(orgId),
        });
      }
      if (projectId) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.documents.byProject(projectId),
        });
      }
      toast.success("Documento eliminado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}
