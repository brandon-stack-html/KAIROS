import api from "./axios-instance";
import { Project, CreateProjectDto } from "@/types/project.types";

export const projectsApi = {
  list: (orgId?: string) =>
    api.get<Project[]>("/projects", {
      params: orgId ? { org_id: orgId } : undefined,
    }),

  getById: (id: string) => api.get<Project>(`/projects/${id}`),

  create: (data: CreateProjectDto) => api.post<Project>("/projects", data),

  getSummary: (id: string) =>
    api.get<{ summary: string }>(`/projects/${id}/summary`),
};
