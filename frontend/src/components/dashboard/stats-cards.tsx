"use client";

import { Building2, ClipboardList, DollarSign, FolderKanban } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardStats } from "@/types/dashboard.types";

interface StatsCardsProps {
  stats: DashboardStats;
}

const formatCurrency = (value: string) =>
  new Intl.NumberFormat("es-MX", { style: "currency", currency: "USD" }).format(
    parseFloat(value)
  );

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Organizaciones
          </CardTitle>
          <Building2 className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-primary">{stats.organizations_count}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Proyectos activos
          </CardTitle>
          <FolderKanban className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-primary">{stats.projects_active}</p>
          <p className="text-xs text-muted-foreground mt-1">
            de {stats.projects_total} totales
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Entregables pendientes
          </CardTitle>
          <ClipboardList className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-primary">{stats.deliverables_pending}</p>
          <p className="text-xs text-muted-foreground mt-1">
            de {stats.deliverables_total} totales
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            Facturación pendiente
          </CardTitle>
          <DollarSign className="size-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold text-primary">
            {formatCurrency(stats.invoices_pending_amount)}
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            de {formatCurrency(stats.invoices_total_amount)} total
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
