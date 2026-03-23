import api from "./axios-instance";
import {
  Organization,
  CreateOrganizationDto,
  Invitation,
  InviteMemberDto,
  ChangeMemberRoleDto,
} from "@/types/organization.types";

export const organizationsApi = {
  list: () => api.get<Organization[]>("/organizations"),

  getById: (id: string) => api.get<Organization>(`/organizations/${id}`),

  create: (data: CreateOrganizationDto) =>
    api.post<Organization>("/organizations", data),

  invite: (orgId: string, data: InviteMemberDto) =>
    api.post<Invitation>(`/organizations/${orgId}/invitations`, data),

  acceptInvitation: (orgId: string, invitationId: string) =>
    api.post<Organization>(
      `/organizations/${orgId}/invitations/${invitationId}/accept`
    ),

  removeMember: (orgId: string, userId: string) =>
    api.delete(`/organizations/${orgId}/members/${userId}`),

  changeMemberRole: (orgId: string, userId: string, data: ChangeMemberRoleDto) =>
    api.patch<Organization>(
      `/organizations/${orgId}/members/${userId}/role`,
      data
    ),
};
