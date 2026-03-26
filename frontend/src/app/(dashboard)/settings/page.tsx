"use client";

import { useCurrentUser } from "@/hooks/use-auth";
import { useAuthStore } from "@/stores/auth.store";
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
import { User, Mail, Shield, Hash } from "lucide-react";

export default function SettingsPage() {
  const { data: currentUser, isLoading } = useCurrentUser();
  const { tenantId } = useAuthStore();

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
          <CardDescription>
            Información de tu cuenta en Kairos
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <User className="size-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Nombre
              </p>
              <p>{currentUser?.name}</p>
            </div>
          </div>
          <Separator />
          <div className="flex items-center gap-3">
            <Mail className="size-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Email
              </p>
              <p>{currentUser?.email}</p>
            </div>
          </div>
          <Separator />
          <div className="flex items-center gap-3">
            <Shield className="size-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Estado
              </p>
              <Badge
                variant={currentUser?.is_active ? "default" : "destructive"}
              >
                {currentUser?.is_active ? "Activa" : "Inactiva"}
              </Badge>
            </div>
          </div>
          <Separator />
          <div className="flex items-center gap-3">
            <Hash className="size-4 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Workspace ID
              </p>
              <p className="font-mono text-sm text-muted-foreground">
                {tenantId?.slice(0, 8)}…
              </p>
            </div>
          </div>
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
