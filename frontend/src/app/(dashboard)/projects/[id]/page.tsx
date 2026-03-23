"use client";

import { useParams } from "next/navigation";
import { useProject } from "@/hooks/use-projects";
import { useOrganization } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { getUserRoleInOrg } from "@/components/shared/role-gate";
import { StatusBadge } from "@/components/shared/status-badge";
import { DeliverableList } from "@/components/deliverables/deliverable-list";
import { ProjectSummary } from "@/components/projects/project-summary";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading: projectLoading } = useProject(id);
  const { data: org } = useOrganization(project?.org_id ?? "");
  const { user } = useAuthStore();

  const userRole =
    user && org ? getUserRoleInOrg(user.id, org.members) : undefined;

  if (projectLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!project) {
    return (
      <p className="text-muted-foreground">Proyecto no encontrado.</p>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              {project.name}
            </h1>
            {project.description && (
              <p className="text-muted-foreground mt-1">
                {project.description}
              </p>
            )}
          </div>
          <StatusBadge status={project.status} />
        </div>
        {org && (
          <Badge variant="outline" className="mt-2">
            {org.name}
          </Badge>
        )}
      </div>

      <Separator />

      <DeliverableList projectId={id} userRole={userRole} />

      <Separator />

      <ProjectSummary projectId={id} />
    </div>
  );
}
