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

  const getBorderColor = () => {
    switch (deliverable.status) {
      case DeliverableStatus.APPROVED:
        return "border-l-4 border-l-green-500";
      case DeliverableStatus.CHANGES_REQUESTED:
        return "border-l-4 border-l-red-500";
      case DeliverableStatus.PENDING:
      default:
        return "border-l-4 border-l-zinc-600";
    }
  };

  return (
    <Card className={`border-white/[0.06] ${getBorderColor()}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base leading-tight text-white">
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
          className="inline-flex items-center gap-1.5 text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          <ExternalLink className="size-3.5" />
          Ver entregable
        </a>

        <div className="flex items-center justify-between">
          <p className="text-xs text-zinc-500 font-mono">
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
                  className="border-red-500/20 hover:border-red-500/40 hover:bg-red-500/10 text-red-400"
                  onClick={() => onRequestChanges(deliverable.id)}
                  disabled={isRequesting}
                >
                  <MessageSquareX className="mr-1.5 size-3.5" />
                  {isRequesting ? "..." : "Cambios"}
                </Button>
                <Button
                  size="sm"
                  className="bg-green-500 text-black hover:bg-green-400"
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
