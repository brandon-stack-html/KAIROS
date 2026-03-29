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
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Bienvenido, {user?.name}
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Aquí tienes un resumen de tu actividad.
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
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Proyectos recientes</h2>
          <Button variant="ghost" size="sm" nativeButton={false} render={<Link href="/projects" />}>
            Ver todos
          </Button>
        </div>
        {recentProjects && recentProjects.length > 0 ? (
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {recentProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <FolderKanban className="size-10 text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">
                No hay proyectos aún. Crea uno para comenzar.
              </p>
            </CardContent>
          </Card>
        )}
      </section>

      {/* Organizations */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tus organizaciones</h2>
          <Button variant="ghost" size="sm" nativeButton={false} render={<Link href="/organizations" />}>
            Ver todas
          </Button>
        </div>
        {organizations && organizations.length > 0 ? (
          <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {organizations.slice(0, 6).map((org) => (
              <OrganizationCard key={org.id} organization={org} />
            ))}
          </div>
        ) : (
          <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-8 text-center">
              <Building2 className="size-10 text-muted-foreground mb-3" />
              <p className="text-sm text-muted-foreground">
                No hay organizaciones aún.
              </p>
            </CardContent>
          </Card>
        )}
      </section>
    </div>
  );
}
