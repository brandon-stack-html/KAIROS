import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/lib/api/auth.api";
import { tenantsApi } from "@/lib/api/tenants.api";
import { useAuthStore } from "@/stores/auth.store";
import { queryKeys } from "@/constants/query-keys";
import { getApiErrorMessage } from "@/lib/api/axios-instance";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { LoginDto, RegisterDto } from "@/types/auth.types";
import { CreateTenantDto } from "@/types/tenant.types";
import { ROUTES } from "@/constants/routes";

export function useCurrentUser() {
  const { isAuthenticated } = useAuthStore();
  return useQuery({
    queryKey: queryKeys.users.me,
    queryFn: () => authApi.getMe().then((res) => res.data),
    enabled: isAuthenticated,
  });
}

export function useTenantBySlug() {
  return useMutation({
    mutationFn: (slug: string) =>
      tenantsApi.getBySlug(slug).then((res) => res.data),
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });
}

export function useCreateTenant() {
  return useMutation({
    mutationFn: (data: CreateTenantDto) =>
      tenantsApi.create(data).then((res) => res.data),
    onSuccess: () => {
      toast.success("Workspace creado");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });
}

export function useLogin() {
  const { login, setUser } = useAuthStore();
  const router = useRouter();

  return useMutation({
    mutationFn: async (data: LoginDto & { tenantId: string }) => {
      const loginRes = await authApi
        .login({ email: data.email, password: data.password })
        .then((res) => res.data);

      login(loginRes.access_token, loginRes.refresh_token, data.tenantId);

      const user = await authApi.getMe().then((res) => res.data);
      setUser(user);

      return { ...loginRes, user };
    },
    onSuccess: () => {
      router.push(ROUTES.DASHBOARD);
      toast.success("Sesión iniciada");
    },
    onError: (error) => {
      useAuthStore.getState().logout();
      toast.error(getApiErrorMessage(error));
    },
  });
}

export function useRegister() {
  const router = useRouter();

  return useMutation({
    mutationFn: (data: RegisterDto) =>
      authApi.register(data).then((res) => res.data),
    onSuccess: () => {
      router.push(ROUTES.LOGIN);
      toast.success("Cuenta creada. Inicia sesión.");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error));
    },
  });
}

export function useLogout() {
  const { refreshToken, logout } = useAuthStore();
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: () => authApi.logout(refreshToken!),
    onSettled: () => {
      logout();
      queryClient.clear();
      router.push(ROUTES.LOGIN);
    },
  });
}
