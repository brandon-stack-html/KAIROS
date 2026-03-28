"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useProjects } from "@/hooks/use-projects";
import { useDeliverables } from "@/hooks/use-deliverables";
import type { Project } from "@/types/project.types";
import { DeliverableStatus } from "@/types/deliverable.types";

function ProjectProgressRow({ project }: { project: Project }) {
  const { data: deliverables, isLoading } = useDeliverables(project.id);

  const total = deliverables?.length ?? 0;
  const approved =
    deliverables?.filter((d) => d.status === DeliverableStatus.APPROVED).length ?? 0;
  const progress = total > 0 ? (approved / total) * 100 : 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="font-medium truncate max-w-[200px]">{project.name}</span>
        <span className="text-muted-foreground text-xs">
          {isLoading ? "..." : `${approved}/${total}`}
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

export function ProjectProgress() {
  const { data: projects, isLoading } = useProjects();

  const topProjects = projects?.slice(0, 5) ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Progreso de proyectos</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <>
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </>
        ) : topProjects.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-4">
            No hay proyectos aún.
          </p>
        ) : (
          topProjects.map((project) => (
            <ProjectProgressRow key={project.id} project={project} />
          ))
        )}
      </CardContent>
    </Card>
  );
}
