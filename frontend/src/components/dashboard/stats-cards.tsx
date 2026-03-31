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
      {/* Organizaciones — Verde */}
      <Card className="border-white/[0.06]">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xs font-medium text-zinc-500 uppercase tracking-widest">
            Organizaciones
          </CardTitle>
          <div className="bg-green-500/10 text-green-400 rounded-lg p-2">
            <Building2 className="size-4" />
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-green-400 font-mono">
            {stats.organizations_count}
          </p>
        </CardContent>
      </Card>

      {/* Proyectos — Amber */}
      <Card className="border-white/[0.06]">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xs font-medium text-zinc-500 uppercase tracking-widest">
            Proyectos activos
          </CardTitle>
          <div className="bg-amber-500/10 text-amber-400 rounded-lg p-2">
            <FolderKanban className="size-4" />
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-amber-400 font-mono">
            {stats.projects_active}
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            de {stats.projects_total} totales
          </p>
        </CardContent>
      </Card>

      {/* Entregables — Azul */}
      <Card className="border-white/[0.06]">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xs font-medium text-zinc-500 uppercase tracking-widest">
            Entregables pendientes
          </CardTitle>
          <div className="bg-blue-500/10 text-blue-400 rounded-lg p-2">
            <ClipboardList className="size-4" />
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-blue-400 font-mono">
            {stats.deliverables_pending}
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            de {stats.deliverables_total} totales
          </p>
        </CardContent>
      </Card>

      {/* Facturación — Verde */}
      <Card className="border-white/[0.06]">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-xs font-medium text-zinc-500 uppercase tracking-widest">
            Facturación pendiente
          </CardTitle>
          <div className="bg-green-500/10 text-green-400 rounded-lg p-2">
            <DollarSign className="size-4" />
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold text-green-400 font-mono">
            {formatCurrency(stats.invoices_pending_amount)}
          </p>
          <p className="text-xs text-zinc-500 mt-1">
            de {formatCurrency(stats.invoices_total_amount)} total
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
