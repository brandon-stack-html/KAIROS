import { Role } from "./auth.types";

export interface Membership {
  user_id: string;
  role: Role;
  joined_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  tenant_id: string;
  is_active: boolean;
  members: Membership[];
}

export interface CreateOrganizationDto {
  name: string;
  slug: string;
}

export interface Invitation {
  id: string;
  org_id: string;
  invitee_email: string;
  role: Role;
  expires_at: string;
  is_accepted: boolean;
}

export interface InviteMemberDto {
  email: string;
  role: Role;
}

export interface ChangeMemberRoleDto {
  role: Role;
}
