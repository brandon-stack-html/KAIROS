export enum Role {
  OWNER = "OWNER",
  ADMIN = "ADMIN",
  MEMBER = "MEMBER",
}

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  is_active: boolean;
}

export interface UpdateProfileDto {
  full_name?: string;
  avatar_url?: string;
}

export interface RegisterDto {
  email: string;
  password: string;
  name: string;
  tenant_id: string;
}

export interface LoginDto {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}

export interface RefreshDto {
  refresh_token: string;
}

export type RefreshResponse = LoginResponse;
