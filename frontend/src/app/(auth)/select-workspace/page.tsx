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
    <Card className="border-border/50">
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-xl">Ingresa a tu workspace</CardTitle>
        <CardDescription>
          Escribe el slug de tu organización para continuar
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onLookup)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="slug">Slug del workspace</Label>
            <Input
              id="slug"
              placeholder="mi-empresa"
              {...register("slug")}
            />
            {errors.slug && (
              <p className="text-sm text-destructive">{errors.slug.message}</p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={tenantBySlug.isPending}
          >
            {tenantBySlug.isPending ? "Buscando..." : "Continuar"}
          </Button>
        </form>

        {notFound && (
          <div className="mt-4 space-y-3 rounded-md border p-4">
            <p className="text-sm text-muted-foreground">
              No se encontró ese workspace. ¿Quieres crearlo?
            </p>
            <Button
              variant="outline"
              className="w-full"
              onClick={onCreateWorkspace}
              disabled={createTenant.isPending}
            >
              {createTenant.isPending ? "Creando..." : "Crear workspace"}
            </Button>
          </div>
        )}

        <div className="mt-6 text-center text-sm text-muted-foreground">
          ¿Ya tienes cuenta?{" "}
          <Link href={ROUTES.LOGIN} className="text-primary hover:text-primary/80 font-medium">
            Inicia sesión
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
