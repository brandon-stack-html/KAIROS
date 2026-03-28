import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { organizationsApi } from "@/lib/api/organizations.api";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import {
  CreateOrganizationDto,
  InviteMemberDto,
  ChangeMemberRoleDto,
} from "@/types/organization.types";

export function useOrganizations() {
  return useQuery({
    queryKey: queryKeys.organizations.list(),
    queryFn: () => organizationsApi.list().then((res) => res.data),
  });
}

export function useOrganization(id: string) {
  return useQuery({
    queryKey: queryKeys.organizations.detail(id),
    queryFn: () => organizationsApi.getById(id).then((res) => res.data),
    enabled: !!id,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateOrganizationDto) =>
      organizationsApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
      toast.success("Organización creada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useInviteMember(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: InviteMemberDto) =>
      organizationsApi.invite(orgId, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.organizations.detail(orgId),
      });
      toast.success("Invitación enviada");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useRemoveMember(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) =>
      organizationsApi.removeMember(orgId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.organizations.detail(orgId),
      });
      toast.success("Miembro eliminado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useChangeMemberRole(orgId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: string;
      data: ChangeMemberRoleDto;
    }) =>
      organizationsApi
        .changeMemberRole(orgId, userId, data)
        .then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.organizations.detail(orgId),
      });
      toast.success("Rol actualizado");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}

export function useAcceptInvitation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: ({
      orgId,
      invitationId,
    }: {
      orgId: string;
      invitationId: string;
    }) =>
      organizationsApi
        .acceptInvitation(orgId, invitationId)
        .then((res) => res.data),
    onSuccess: (_, { orgId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.organizations.all });
      router.push(`/organizations/${orgId}`);
      toast.success("Te uniste a la organización");
    },
    onError: (error) => toast.error(getApiErrorMessage(error)),
  });
}
