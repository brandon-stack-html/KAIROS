export enum Role {
  OWNER = "OWNER",
  ADMIN = "ADMIN",
  MEMBER = "MEMBER",
}

export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
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
