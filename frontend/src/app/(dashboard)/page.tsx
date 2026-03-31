"use client";

import { useCurrentUser } from "@/hooks/use-auth";
import { useOrganizations } from "@/hooks/use-organizations";
import { useProjects } from "@/hooks/use-projects";
import { useDashboardStats } from "@/hooks/use-dashboard";
import { StatsCards } from "@/components/dashboard/stats-cards";
import { DeliverableChart } from "@/components/dashboard/deliverable-chart";
import { InvoiceChart } from "@/components/dashboard/invoice-chart";
import { ProjectProgress } from "@/components/dashboard/project-progress";
import { ProjectCard } from "@/components/projects/project-card";
import { OrganizationCard } from "@/components/organizations/organization-card";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Building2, FolderKanban } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { data: user } = useCurrentUser();
  const { data: organizations } = useOrganizations();
  const { data: projects } = useProjects();
  const { data: stats, isLoading: statsLoading } = useDashboardStats();

  const recentProjects = projects
    ?.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  const today = new Date().toLocaleDateString("es-MX", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">
          Bienvenido, {user?.name}
        </h1>
        <p className="text-sm text-zinc-500 mt-2 font-mono">
          {today}
        </p>
      </div>

      {/* Stats cards */}
      {statsLoading ? (
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      ) : stats ? (
        <StatsCards stats={stats} />
      ) : null}

      {/* Charts + Progress */}
      {stats && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <DeliverableChart stats={stats} />
          <InvoiceChart stats={stats} />
          <ProjectProgress />
        </div>
      )}
      {!stats && <ProjectProgress />}

      {/* Recent projects */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Proyectos recientes</h2>
          <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-200 h-auto p-0" nativeButton={false} render={<Link href="/projects" />}>
            Ver todos
          </Button>
        </div>
        {recentProjects && recentProjects.length > 0 ? (
          <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {recentProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={FolderKanban}
            title="No hay proyectos aún"
            description="Crea un proyecto para comenzar a colaborar con clientes."
            action={
              <Button nativeButton={false} render={<Link href="/projects/new" />} className="bg-green-500 text-black hover:bg-green-400">
                Crear proyecto
              </Button>
            }
          />
        )}
      </section>

      {/* Organizations */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tus organizaciones</h2>
          <Button variant="ghost" size="sm" className="text-zinc-400 hover:text-zinc-200 h-auto p-0" nativeButton={false} render={<Link href="/organizations" />}>
            Ver todas
          </Button>
        </div>
        {organizations && organizations.length > 0 ? (
          <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {organizations.slice(0, 6).map((org) => (
              <OrganizationCard key={org.id} organization={org} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Building2}
            title="No hay organizaciones aún"
            description="Crea una organización para empezar a trabajar con clientes."
            action={
              <Button nativeButton={false} render={<Link href="/organizations/new" />} className="bg-green-500 text-black hover:bg-green-400">
                Crear organización
              </Button>
            }
          />
        )}
      </section>
    </div>
  );
}
