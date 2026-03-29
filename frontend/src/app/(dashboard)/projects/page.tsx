"use client";

import { useState } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/use-projects";
import { useOrganizations } from "@/hooks/use-organizations";
import { ProjectCard } from "@/components/projects/project-card";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FolderKanban, Plus } from "lucide-react";

const ALL_ORGS = "__all__";

export default function ProjectsPage() {
  const [selectedOrg, setSelectedOrg] = useState<string>(ALL_ORGS);
  const orgFilter = selectedOrg === ALL_ORGS ? undefined : selectedOrg;

  const { data: projects, isLoading } = useProjects(orgFilter);
  const { data: organizations } = useOrganizations();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Proyectos</h1>
        <Button nativeButton={false} render={<Link href="/projects/new" />}>
          <Plus className="mr-2 size-4" />
          Nuevo proyecto
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-sm text-muted-foreground">Filtrar por org:</span>
        <Select value={selectedOrg} onValueChange={(v) => v && setSelectedOrg(v)}>
          <SelectTrigger className="w-64">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={ALL_ORGS}>Todas las organizaciones</SelectItem>
            {organizations?.map((org) => (
              <SelectItem key={org.id} value={org.id}>
                {org.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-36" />
          ))}
        </div>
      ) : projects?.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="Sin proyectos"
          description={
            orgFilter
              ? "Esta organización no tiene proyectos aún."
              : "Crea tu primer proyecto para comenzar a gestionar entregables."
          }
          action={
            <Button nativeButton={false} render={<Link href="/projects/new" />}>
              <Plus className="mr-2 size-4" />
              Crear proyecto
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
