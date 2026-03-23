import api from "./axios-instance";
import {
  RegisterDto,
  LoginDto,
  LoginResponse,
  User,
} from "@/types/auth.types";

export const authApi = {
  register: (data: RegisterDto) => api.post<User>("/users/", data),

  login: (data: LoginDto) => api.post<LoginResponse>("/auth/login", data),

  refresh: (refreshToken: string) =>
    api.post<LoginResponse>("/auth/refresh", { refresh_token: refreshToken }),

  logout: (refreshToken: string) =>
    api.post("/auth/logout", { refresh_token: refreshToken }),

  getMe: () => api.get<User>("/users/me"),
};
