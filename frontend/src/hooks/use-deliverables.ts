import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { deliverablesApi, AiFeedbackResponse } from "@/lib/api/deliverables.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import { CreateDeliverableDto } from "@/types/deliverable.types";

export function useDeliverables(projectId: string) {
  return useQuery({
    queryKey: queryKeys.deliverables.byProject(projectId),
    queryFn: () =>
      deliverablesApi.listByProject(projectId).then((res) => res.data),
    enabled: !!projectId,
  });
}

export function useSubmitDeliverable(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateDeliverableDto) =>
      deliverablesApi.submit(projectId, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.deliverables.byProject(projectId),
      });
      toast.success("Entregable enviado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useApproveDeliverable(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      deliverablesApi.approve(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.deliverables.byProject(projectId),
      });
      toast.success("Entregable aprobado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useRequestChanges(projectId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      deliverablesApi.requestChanges(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.deliverables.byProject(projectId),
      });
      toast.success("Cambios solicitados");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useGenerateFeedback() {
  return useMutation({
    mutationFn: ({
      id,
      feedbackText,
    }: {
      id: string;
      feedbackText: string;
    }): Promise<AiFeedbackResponse> =>
      deliverablesApi.generateFeedback(id, feedbackText).then((res) => res.data),
    onError: (error) => {
      console.warn("AI feedback generation failed", error);
      // Don't show toast here — let parent component handle it as non-blocking
    },
  });
}
