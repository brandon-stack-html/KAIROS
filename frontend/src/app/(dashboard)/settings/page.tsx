"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod/v4";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useTheme } from "next-themes";
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
import { Shield, Hash, Sun, Moon, Monitor } from "lucide-react";

const schema = z.object({
  full_name: z.string().min(2).max(100),
  avatar_url: z.string().url().max(2048).or(z.literal("")).optional(),
});

type FormValues = z.infer<typeof schema>;

const THEME_OPTIONS = [
  { value: "light", label: "Claro", icon: Sun },
  { value: "dark", label: "Oscuro", icon: Moon },
  { value: "system", label: "Sistema", icon: Monitor },
] as const;

export default function SettingsPage() {
  const { data: currentUser, isLoading } = useCurrentUser();
  const { tenantId } = useAuthStore();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const { theme, setTheme } = useTheme();

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
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Configuración</h1>
        <p className="text-sm text-zinc-500 mt-1">
          Administra tu perfil y preferencias.
        </p>
      </div>

      <Card className="border-white/[0.06]">
        <CardHeader>
          <CardTitle>Perfil</CardTitle>
          <CardDescription className="text-zinc-500">Información de tu cuenta en Kairos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {editing ? (
            <form onSubmit={handleSubmit((v) => mutation.mutate(v))} className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="full_name" className="text-zinc-300">Nombre</Label>
                <Input id="full_name" className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600" {...register("full_name")} />
                {errors.full_name && (
                  <p className="text-sm text-red-400">{errors.full_name.message}</p>
                )}
              </div>
              <div className="space-y-1">
                <Label htmlFor="avatar_url" className="text-zinc-300">URL de avatar</Label>
                <Input
                  id="avatar_url"
                  className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600"
                  placeholder="https://example.com/avatar.png"
                  {...register("avatar_url")}
                />
                {errors.avatar_url && (
                  <p className="text-sm text-red-400">{errors.avatar_url.message}</p>
                )}
              </div>
              <div className="flex gap-2 pt-1">
                <Button type="submit" className="bg-green-500 text-black hover:bg-green-400" disabled={mutation.isPending}>
                  {mutation.isPending ? "Guardando…" : "Guardar"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  className="border-white/[0.06] hover:bg-white/[0.04]"
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
                    <p className="text-sm font-medium text-zinc-500">Nombre</p>
                    <p className="text-white">{currentUser?.name}</p>
                  </div>
                  <Separator className="bg-white/[0.06]" />
                  <div>
                    <p className="text-sm font-medium text-zinc-500">Email</p>
                    <p className="text-zinc-300 font-mono">{currentUser?.email}</p>
                  </div>
                  {currentUser?.avatar_url && (
                    <>
                      <Separator className="bg-white/[0.06]" />
                      <div>
                        <p className="text-sm font-medium text-zinc-500">Avatar</p>
                        <p className="text-sm text-zinc-500 truncate max-w-xs">
                          {currentUser.avatar_url}
                        </p>
                      </div>
                    </>
                  )}
                  <Separator className="bg-white/[0.06]" />
                  <div className="flex items-center gap-2">
                    <Shield className="size-4 text-zinc-500" />
                    <div>
                      <p className="text-sm font-medium text-zinc-500">Estado</p>
                      <Badge variant={currentUser?.is_active ? "default" : "destructive"} className={currentUser?.is_active ? "bg-green-500/10 text-green-400 border-green-500/20" : ""}>
                        {currentUser?.is_active ? "Activa" : "Inactiva"}
                      </Badge>
                    </div>
                  </div>
                  <Separator className="bg-white/[0.06]" />
                  <div className="flex items-center gap-2">
                    <Hash className="size-4 text-zinc-500" />
                    <div>
                      <p className="text-sm font-medium text-zinc-500">Workspace ID</p>
                      <p className="font-mono text-sm text-zinc-500">
                        {tenantId?.slice(0, 8)}…
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <Button variant="outline" className="border-white/[0.06] hover:bg-white/[0.04]" onClick={() => setEditing(true)}>
                Editar perfil
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="border-white/[0.06]">
        <CardHeader>
          <CardTitle>Preferencias</CardTitle>
          <CardDescription className="text-zinc-500">Personaliza tu experiencia en Kairos</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Label className="text-zinc-300">Tema</Label>
          <div className="flex gap-2">
            {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
              <Button
                key={value}
                variant={theme === value ? "default" : "outline"}
                size="sm"
                onClick={() => setTheme(value)}
                className={`flex items-center gap-2 ${
                  theme === value
                    ? "bg-white/[0.04] border-white/[0.06] text-white"
                    : "border-white/[0.06] text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.02]"
                }`}
              >
                <Icon className="size-4" />
                {label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card className="border-white/[0.06]">
        <CardHeader>
          <CardTitle>Sobre Kairos</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-zinc-500">
            Kairos es un portal de clientes para freelancers. Gestiona tus
            organizaciones, proyectos, entregables y facturas en un solo lugar.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
