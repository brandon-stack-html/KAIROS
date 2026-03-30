import api from "./axios-instance";
import { Deliverable, CreateDeliverableDto } from "@/types/deliverable.types";

export interface AiFeedbackResponse {
  deliverable_id: string;
  feedback_text: string;
  ai_structured_feedback: string;
}

export const deliverablesApi = {
  listByProject: (projectId: string) =>
    api.get<Deliverable[]>(`/projects/${projectId}/deliverables`),

  submit: (projectId: string, data: CreateDeliverableDto) =>
    api.post<Deliverable>(`/projects/${projectId}/deliverables`, data),

  approve: (id: string) =>
    api.patch<Deliverable>(`/deliverables/${id}/approve`),

  requestChanges: (id: string) =>
    api.patch<Deliverable>(`/deliverables/${id}/request-changes`),

  generateFeedback: (id: string, feedbackText: string) =>
    api.post<AiFeedbackResponse>(`/deliverables/${id}/ai-feedback`, {
      feedback_text: feedbackText,
    }),
};
