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
  const initials = project.name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  // Calculate progress: completed if status is COMPLETED, 50% if active
  const progress = project.status === "COMPLETED" ? 100 : project.status === "ACTIVE" ? 50 : 25;

  return (
    <Link href={`/projects/${project.id}`}>
      <Card className="border-white/[0.06] transition-all duration-200 hover:border-white/[0.1] hover:bg-white/[0.02] cursor-pointer h-full">
        <CardHeader className="pb-2">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-green-500/10 text-green-400 font-bold text-sm flex items-center justify-center shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg leading-tight">
                {project.name}
              </CardTitle>
              <div className="flex items-center justify-between gap-2 mt-1">
                <p className="text-xs font-mono text-zinc-500">
                  {format(new Date(project.created_at), "d MMM", {
                    locale: es,
                  })}
                </p>
                <StatusBadge status={project.status} />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {project.description && (
            <p className="text-sm text-zinc-400 line-clamp-2">
              {project.description}
            </p>
          )}
          {/* Progress bar */}
          <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
            <div
              className="h-full bg-green-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
