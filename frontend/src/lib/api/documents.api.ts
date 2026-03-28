import api from "./axios-instance";
import { Document } from "@/types/document.types";

export const documentsApi = {
  listByOrg: (orgId: string) =>
    api.get<Document[]>(`/organizations/${orgId}/documents`),

  listByProject: (projectId: string) =>
    api.get<Document[]>(`/projects/${projectId}/documents`),

  uploadToOrg: (orgId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<Document>(`/organizations/${orgId}/documents`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  uploadToProject: (projectId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<Document>(`/projects/${projectId}/documents`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  delete: (documentId: string) =>
    api.delete(`/documents/${documentId}`),

  downloadUrl: (documentId: string) =>
    `/api/v1/documents/${documentId}/download`,
};
