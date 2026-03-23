"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Project } from "@/types/project.types";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="transition-colors hover:bg-accent/50 cursor-pointer h-full">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-lg leading-tight">
              {project.name}
            </CardTitle>
            <StatusBadge status={project.status} />
          </div>
        </CardHeader>
        <CardContent>
          {project.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
              {project.description}
            </p>
          )}
          <p className="text-xs text-muted-foreground">
            {format(new Date(project.created_at), "d MMM yyyy", {
              locale: es,
            })}
          </p>
        </CardContent>
      </Card>
    </Link>
  );
}
