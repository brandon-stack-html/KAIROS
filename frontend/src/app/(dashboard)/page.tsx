"use client";

import { useAuthStore } from "@/stores/auth.store";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Building2, FolderKanban, FileCheck, Receipt } from "lucide-react";

const stats = [
  {
    label: "Organizaciones",
    value: "—",
    icon: Building2,
    description: "Tus organizaciones",
  },
  {
    label: "Proyectos",
    value: "—",
    icon: FolderKanban,
    description: "Proyectos activos",
  },
  {
    label: "Entregables",
    value: "—",
    icon: FileCheck,
    description: "Pendientes de revisión",
  },
  {
    label: "Facturas",
    value: "—",
    icon: Receipt,
    description: "Facturas emitidas",
  },
];

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">
          Bienvenido, {user?.name ?? "usuario"}
        </h1>
        <p className="text-muted-foreground">
          Resumen de tu actividad en Kairos
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.label}
              </CardTitle>
              <stat.icon className="size-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <CardDescription>{stat.description}</CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
