import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { conversationsApi, ActionItemsResponse } from "@/lib/api/conversations.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import type { SendMessageDto } from "@/types/conversation.types";

// ── Queries ──────────────────────────────────────────────────────────

export function useOrgConversations(orgId: string) {
  return useQuery({
    queryKey: queryKeys.conversations.byOrg(orgId),
    queryFn: () => conversationsApi.listByOrg(orgId).then((res) => res.data),
    enabled: !!orgId,
  });
}

export function useConversation(id: string) {
  return useQuery({
    queryKey: queryKeys.conversations.detail(id),
    queryFn: () => conversationsApi.getById(id).then((res) => res.data),
    enabled: !!id,
  });
}

export function useMessages(conversationId: string, page = 1, limit = 50) {
  return useQuery({
    queryKey: [...queryKeys.conversations.messages(conversationId), page],
    queryFn: () =>
      conversationsApi
        .listMessages(conversationId, page, limit)
        .then((res) => res.data),
    enabled: !!conversationId,
    refetchInterval: 10_000,
  });
}

// ── Mutations ────────────────────────────────────────────────────────

export function useCreateOrgConversation(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      conversationsApi.createForOrg(orgId).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.conversations.byOrg(orgId),
      });
      toast.success("Conversación creada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useCreateProjectConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: string) =>
      conversationsApi.createForProject(projectId).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.conversations.all,
      });
      toast.success("Conversación creada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SendMessageDto) =>
      conversationsApi
        .sendMessage(conversationId, data)
        .then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.conversations.messages(conversationId),
      });
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useDeleteMessage(conversationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (messageId: string) =>
      conversationsApi.deleteMessage(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.conversations.messages(conversationId),
      });
      toast.success("Mensaje eliminado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useExtractActions(conversationId: string) {
  return useMutation({
    mutationFn: (): Promise<ActionItemsResponse> =>
      conversationsApi.extractActions(conversationId).then((res) => res.data),
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}
