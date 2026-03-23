"use client";

import { useState } from "react";
import {
  useDeliverables,
  useApproveDeliverable,
  useRequestChanges,
} from "@/hooks/use-deliverables";
import { DeliverableCard } from "./deliverable-card";
import { DeliverableForm } from "./deliverable-form";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PackagePlus, FileBox } from "lucide-react";
import { Role } from "@/types/auth.types";

interface DeliverableListProps {
  projectId: string;
  userRole: Role | undefined;
}

export function DeliverableList({ projectId, userRole }: DeliverableListProps) {
  const { data: deliverables, isLoading } = useDeliverables(projectId);
  const approveMutation = useApproveDeliverable(projectId);
  const requestChangesMutation = useRequestChanges(projectId);
  const [formOpen, setFormOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          Entregables ({deliverables?.length ?? 0})
        </h2>
        <Button size="sm" onClick={() => setFormOpen(true)}>
          <PackagePlus className="mr-2 size-4" />
          Enviar entregable
        </Button>
      </div>

      {deliverables?.length === 0 ? (
        <EmptyState
          icon={FileBox}
          title="Sin entregables"
          description="Aún no se han enviado entregables para este proyecto."
          action={
            <Button size="sm" onClick={() => setFormOpen(true)}>
              <PackagePlus className="mr-2 size-4" />
              Enviar el primero
            </Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {deliverables?.map((deliverable) => (
            <DeliverableCard
              key={deliverable.id}
              deliverable={deliverable}
              userRole={userRole}
              onApprove={(id) => approveMutation.mutate(id)}
              onRequestChanges={(id) => requestChangesMutation.mutate(id)}
              isApproving={approveMutation.isPending}
              isRequesting={requestChangesMutation.isPending}
            />
          ))}
        </div>
      )}

      <DeliverableForm
        projectId={projectId}
        open={formOpen}
        onOpenChange={setFormOpen}
      />
    </div>
  );
}
