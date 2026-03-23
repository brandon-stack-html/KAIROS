"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ProjectForm } from "@/components/projects/project-form";
import { Skeleton } from "@/components/ui/skeleton";

function NewProjectContent() {
  const searchParams = useSearchParams();
  const defaultOrgId = searchParams.get("org_id") ?? undefined;

  return (
    <div className="max-w-lg">
      <Card>
        <CardHeader>
          <CardTitle>Nuevo proyecto</CardTitle>
          <CardDescription>
            Crea un proyecto dentro de una organización para gestionar
            entregables
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProjectForm defaultOrgId={defaultOrgId} />
        </CardContent>
      </Card>
    </div>
  );
}

export default function NewProjectPage() {
  return (
    <Suspense fallback={<Skeleton className="h-64 max-w-lg" />}>
      <NewProjectContent />
    </Suspense>
  );
}
