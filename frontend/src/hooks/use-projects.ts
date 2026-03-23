import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "@/lib/api/projects.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import { CreateProjectDto } from "@/types/project.types";

export function useProjects(orgId?: string) {
  return useQuery({
    queryKey: queryKeys.projects.list(orgId),
    queryFn: () => projectsApi.list(orgId).then((res) => res.data),
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.detail(id),
    queryFn: () => projectsApi.getById(id).then((res) => res.data),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateProjectDto) =>
      projectsApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.projects.all });
      toast.success("Proyecto creado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useProjectSummary(id: string) {
  return useQuery({
    queryKey: queryKeys.projects.summary(id),
    queryFn: () => projectsApi.getSummary(id).then((res) => res.data),
    enabled: false,
  });
}
