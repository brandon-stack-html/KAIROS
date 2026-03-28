import api from "./axios-instance";
import type {
  Conversation,
  Message,
  SendMessageDto,
} from "@/types/conversation.types";

export const conversationsApi = {
  createForOrg: (orgId: string) =>
    api.post<Conversation>(`/organizations/${orgId}/conversations`),

  createForProject: (projectId: string) =>
    api.post<Conversation>(`/projects/${projectId}/conversations`),

  listByOrg: (orgId: string) =>
    api.get<Conversation[]>(`/organizations/${orgId}/conversations`),

  getById: (id: string) =>
    api.get<Conversation>(`/conversations/${id}`),

  sendMessage: (conversationId: string, data: SendMessageDto) =>
    api.post<Message>(`/conversations/${conversationId}/messages`, data),

  listMessages: (conversationId: string, page = 1, limit = 50) =>
    api.get<Message[]>(`/conversations/${conversationId}/messages`, {
      params: { page, limit },
    }),

  deleteMessage: (messageId: string) =>
    api.delete(`/messages/${messageId}`),
};
