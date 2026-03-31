"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { workspaceSchema, WorkspaceFormData } from "@/lib/validators/auth.schema";
import { useTenantBySlug, useCreateTenant } from "@/hooks/use-auth";
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
import { useState } from "react";
import Link from "next/link";

export default function SelectWorkspacePage() {
  const router = useRouter();
  const { setTenantId } = useAuthStore();
  const tenantBySlug = useTenantBySlug();
  const createTenant = useCreateTenant();
  const [notFound, setNotFound] = useState(false);

  const {
    register,
    handleSubmit,
    getValues,
    formState: { errors },
  } = useForm<WorkspaceFormData>({
    resolver: zodResolver(workspaceSchema),
  });

  const onLookup = (data: WorkspaceFormData) => {
    setNotFound(false);
    tenantBySlug.mutate(data.slug, {
      onSuccess: (tenant) => {
        setTenantId(tenant.id);
        router.push(ROUTES.LOGIN);
      },
      onError: () => {
        setNotFound(true);
      },
    });
  };

  const onCreateWorkspace = () => {
    const slug = getValues("slug");
    createTenant.mutate(
      { name: slug, slug },
      {
        onSuccess: (tenant) => {
          setTenantId(tenant.id);
          router.push(ROUTES.REGISTER);
        },
      }
    );
  };

  return (
    <Card className="border-white/[0.06] bg-white/[0.02] shadow-none p-8">
      <CardHeader className="space-y-1 pb-6 px-0 pt-0">
        <CardTitle className="text-xl font-semibold">Ingresa a tu workspace</CardTitle>
        <CardDescription className="text-zinc-500">
          Escribe el slug de tu organización para continuar
        </CardDescription>
      </CardHeader>
      <CardContent className="px-0">
        <form onSubmit={handleSubmit(onLookup)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="slug" className="text-zinc-300">Slug del workspace</Label>
            <Input
              id="slug"
              placeholder="mi-empresa"
              className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 focus:ring-green-500/20"
              {...register("slug")}
            />
            {errors.slug && (
              <p className="text-sm text-red-400">{errors.slug.message}</p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full bg-green-500 text-black font-medium hover:bg-green-400 transition-colors duration-150 mt-6"
            disabled={tenantBySlug.isPending}
          >
            {tenantBySlug.isPending ? "Buscando..." : "Continuar"}
          </Button>
        </form>

        {notFound && (
          <div className="mt-4 space-y-3 rounded-lg border border-white/[0.06] bg-white/[0.02] p-4">
            <p className="text-sm text-zinc-400">
              No se encontró ese workspace. ¿Quieres crearlo?
            </p>
            <Button
              variant="outline"
              className="w-full border-white/[0.06] hover:bg-white/[0.04] text-zinc-300"
              onClick={onCreateWorkspace}
              disabled={createTenant.isPending}
            >
              {createTenant.isPending ? "Creando..." : "Crear workspace"}
            </Button>
          </div>
        )}

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
