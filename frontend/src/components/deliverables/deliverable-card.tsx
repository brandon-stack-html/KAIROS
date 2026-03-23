"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import { RoleGate } from "@/components/shared/role-gate";
import { Deliverable, DeliverableStatus } from "@/types/deliverable.types";
import { Role } from "@/types/auth.types";
import { ExternalLink, Check, MessageSquareX } from "lucide-react";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface DeliverableCardProps {
  deliverable: Deliverable;
  userRole: Role | undefined;
  onApprove: (id: string) => void;
  onRequestChanges: (id: string) => void;
  isApproving: boolean;
  isRequesting: boolean;
}

export function DeliverableCard({
  deliverable,
  userRole,
  onApprove,
  onRequestChanges,
  isApproving,
  isRequesting,
}: DeliverableCardProps) {
  const isPending = deliverable.status === DeliverableStatus.PENDING;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base leading-tight">
            {deliverable.title}
          </CardTitle>
          <StatusBadge status={deliverable.status} />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <a
          href={deliverable.url_link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 text-sm text-primary hover:underline"
        >
          <ExternalLink className="size-3.5" />
          Ver entregable
        </a>

        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            {format(new Date(deliverable.created_at), "d MMM yyyy, HH:mm", {
              locale: es,
            })}
          </p>

          {isPending && (
            <RoleGate
              allowedRoles={[Role.OWNER, Role.ADMIN]}
              userRole={userRole}
            >
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onRequestChanges(deliverable.id)}
                  disabled={isRequesting}
                >
                  <MessageSquareX className="mr-1.5 size-3.5" />
                  {isRequesting ? "..." : "Cambios"}
                </Button>
                <Button
                  size="sm"
                  onClick={() => onApprove(deliverable.id)}
                  disabled={isApproving}
                >
                  <Check className="mr-1.5 size-3.5" />
                  {isApproving ? "..." : "Aprobar"}
                </Button>
              </div>
            </RoleGate>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
