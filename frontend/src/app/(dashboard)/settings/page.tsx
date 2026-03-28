"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useCurrentUser } from "@/hooks/use-auth";
import { useAuthStore } from "@/stores/auth.store";
import { authApi } from "@/lib/api/auth.api";
import { queryKeys } from "@/constants/query-keys";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Shield, Hash } from "lucide-react";

const schema = z.object({
  full_name: z.string().min(2).max(100),
  avatar_url: z.string().url().max(2048).or(z.literal("")).optional(),
});

type FormValues = z.infer<typeof schema>;

export default function SettingsPage() {
  const { data: currentUser, isLoading } = useCurrentUser();
  const { tenantId } = useAuthStore();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: {
      full_name: currentUser?.name ?? "",
      avatar_url: currentUser?.avatar_url ?? "",
    },
  });

  const mutation = useMutation({
    mutationFn: (data: FormValues) =>
      authApi.updateProfile({
        full_name: data.full_name,
        avatar_url: data.avatar_url || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.users.me });
      setEditing(false);
      toast.success("Perfil actualizado");
    },
    onError: () => {
      toast.error("Error al actualizar el perfil");
    },
  });

  if (isLoading) {
    return (
      <div className="max-w-lg space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Configuración</h1>

      <Card>
        <CardHeader>
          <CardTitle>Perfil</CardTitle>
          <CardDescription>Información de tu cuenta en Kairos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {editing ? (
            <form onSubmit={handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="full_name">Nombre</Label>
                <Input id="full_name" {...register("full_name")} />
                {errors.full_name && (
                  <p className="text-sm text-destructive">{errors.full_name.message}</p>
                )}
              </div>
              <div className="space-y-1">
                <Label htmlFor="avatar_url">URL de avatar</Label>
                <Input
                  id="avatar_url"
                  placeholder="https://example.com/avatar.png"
                  {...register("avatar_url")}
                />
                {errors.avatar_url && (
                  <p className="text-sm text-destructive">{errors.avatar_url.message}</p>
                )}
              </div>
              <div className="flex gap-2 pt-1">
                <Button type="submit" disabled={mutation.isPending}>
                  {mutation.isPending ? "Guardando…" : "Guardar"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setEditing(false);
                    reset();
                  }}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          ) : (
            <>
              <div className="flex items-start justify-between">
                <div className="space-y-3 flex-1">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Nombre</p>
                    <p>{currentUser?.name}</p>
                  </div>
                  <Separator />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Email</p>
                    <p>{currentUser?.email}</p>
                  </div>
                  {currentUser?.avatar_url && (
                    <>
                      <Separator />
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Avatar</p>
                        <p className="text-sm text-muted-foreground truncate max-w-xs">
                          {currentUser.avatar_url}
                        </p>
                      </div>
                    </>
                  )}
                  <Separator />
                  <div className="flex items-center gap-2">
                    <Shield className="size-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Estado</p>
                      <Badge variant={currentUser?.is_active ? "default" : "destructive"}>
                        {currentUser?.is_active ? "Activa" : "Inactiva"}
                      </Badge>
                    </div>
                  </div>
                  <Separator />
                  <div className="flex items-center gap-2">
                    <Hash className="size-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Workspace ID</p>
                      <p className="font-mono text-sm text-muted-foreground">
                        {tenantId?.slice(0, 8)}…
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <Button variant="outline" onClick={() => setEditing(true)}>
                Editar perfil
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sobre Kairos</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Kairos es un portal de clientes para freelancers. Gestiona tus
            organizaciones, proyectos, entregables y facturas en un solo lugar.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
