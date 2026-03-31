"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema, RegisterFormData } from "@/lib/validators/auth.schema";
import { useRegister } from "@/hooks/use-auth";
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

export default function RegisterPage() {
  const router = useRouter();
  const { tenantId } = useAuthStore();
  const registerMutation = useRegister();

  useEffect(() => {
    if (!tenantId) {
      router.push(ROUTES.SELECT_WORKSPACE);
    }
  }, [tenantId, router]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      tenant_id: tenantId ?? "",
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    registerMutation.mutate({
      name: data.name,
      email: data.email,
      password: data.password,
      tenant_id: data.tenant_id,
    });
  };

  if (!tenantId) return null;

  return (
    <Card className="border-white/[0.06] bg-white/[0.02] shadow-none p-8">
      <CardHeader className="space-y-1 pb-6 px-0 pt-0">
        <CardTitle className="text-xl font-semibold">Crear cuenta</CardTitle>
        <CardDescription className="text-zinc-500">
          Completa tus datos para registrarte
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-zinc-300">Nombre completo</Label>
            <Input
              id="name"
              placeholder="Juan Pérez"
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("name")}
            />
            {errors.name && (
              <p className="text-sm text-red-400">
                {errors.name.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email" className="text-zinc-300">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="tu@email.com"
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
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("password")}
            />
            {errors.password && (
              <p className="text-sm text-red-400">
                {errors.password.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword" className="text-zinc-300">Confirmar contraseña</Label>
            <Input
              id="confirmPassword"
              type="password"
              placeholder="••••••••"
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("confirmPassword")}
            />
            {errors.confirmPassword && (
              <p className="text-sm text-red-400">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-green-500 text-black font-medium hover:bg-green-400 transition-colors duration-150 mt-6"
            disabled={registerMutation.isPending}
          >
            {registerMutation.isPending ? "Creando cuenta..." : "Registrarse"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-zinc-500">
          ¿Ya tienes cuenta?{" "}
          <Link href={ROUTES.LOGIN} className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors duration-150">
            Inicia sesión
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
