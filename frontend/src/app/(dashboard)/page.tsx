"use client";

import { useCurrentUser } from "@/hooks/use-auth";
import { useOrganizations } from "@/hooks/use-organizations";
import { useProjects } from "@/hooks/use-projects";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ProjectCard } from "@/components/projects/project-card";
import { OrganizationCard } from "@/components/organizations/organization-card";
import { Building2, FolderKanban, Plus } from "lucide-react";
import Link from "next/link";
import { ProjectStatus } from "@/types/project.types";

export default function DashboardPage() {
  const { data: user, isLoading: userLoading } = useCurrentUser();
  const { data: organizations, isLoading: orgsLoading } = useOrganizations();
  const { data: projects, isLoading: projectsLoading } = useProjects();

  const isLoading = userLoading || orgsLoading || projectsLoading;

  const totalOrgs = organizations?.length ?? 0;
  const totalProjects = projects?.length ?? 0;
  const activeProjects =
    projects?.filter((p) => p.status === ProjectStatus.ACTIVE).length ?? 0;

  const recentProjects = projects
    ?.sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 5);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">
        Bienvenido, {user?.name}
      </h1>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Organizaciones
            </CardTitle>
            <Building2 className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{totalOrgs}</p>
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
            <p className="text-2xl font-bold">{activeProjects}</p>
            <p className="text-xs text-muted-foreground">
              de {totalProjects} totales
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Acciones rápidas
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <Button
              size="sm"
              variant="outline"
              className="justify-start"
              render={<Link href="/organizations/new" />}
            >
              <Plus className="mr-2 size-3.5" />
              Nueva organización
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="justify-start"
              render={<Link href="/projects/new" />}
            >
              <Plus className="mr-2 size-3.5" />
              Nuevo proyecto
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Proyectos recientes */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Proyectos recientes</h2>
          <Button variant="ghost" size="sm" render={<Link href="/projects" />}>
            Ver todos
          </Button>
        </div>
        {recentProjects && recentProjects.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
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
      </div>

      {/* Organizaciones */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tus organizaciones</h2>
          <Button variant="ghost" size="sm" render={<Link href="/organizations" />}>
            Ver todas
          </Button>
        </div>
        {organizations && organizations.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
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
      </div>
    </div>
  );
}
