"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, LoginFormData } from "@/lib/validators/auth.schema";
import { useLogin } from "@/hooks/use-auth";
import { useAuthStore } from "@/stores/auth.store";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/constants/routes";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link";
import { useEffect } from "react";

export default function LoginPage() {
  const router = useRouter();
  const { tenantId } = useAuthStore();
  const loginMutation = useLogin();

  useEffect(() => {
    if (!tenantId) {
      router.push(ROUTES.SELECT_WORKSPACE);
    }
  }, [tenantId, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = (data: LoginFormData) => {
    if (!tenantId) return;
    loginMutation.mutate({ ...data, tenantId });
  };

  if (!tenantId) return null;

  return (
    <Card className="border-white/[0.06] bg-white/[0.02] shadow-none p-8">
      <CardHeader className="space-y-1 pb-6 px-0 pt-0">
        <CardTitle className="text-xl font-semibold">Iniciar sesión</CardTitle>
        <CardDescription className="text-zinc-500">
          Ingresa tus credenciales para continuar
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-zinc-300">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="tu@email.com"
              autoComplete="email"
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("email")}
            />
            {errors.email && (
              <p className="text-sm text-red-400">
                {errors.email.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-zinc-300">Contraseña</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("password")}
            />
            {errors.password && (
              <p className="text-sm text-red-400">
                {errors.password.message}
              </p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-green-500 text-black font-medium hover:bg-green-400 transition-colors duration-150 mt-6"
            disabled={loginMutation.isPending}
          >
            {loginMutation.isPending ? "Ingresando..." : "Iniciar sesión"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-zinc-500">
          ¿No tienes cuenta?{" "}
          <Link href={ROUTES.REGISTER} className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors duration-150">
            Regístrate
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
