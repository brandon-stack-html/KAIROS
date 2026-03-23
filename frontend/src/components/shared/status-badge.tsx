"use client";

import { Badge } from "@/components/ui/badge";
import { DeliverableStatus } from "@/types/deliverable.types";
import { InvoiceStatus } from "@/types/invoice.types";
import { ProjectStatus } from "@/types/project.types";

type Status = DeliverableStatus | InvoiceStatus | ProjectStatus;

const statusConfig: Record<
  Status,
  {
    label: string;
    variant: "default" | "secondary" | "destructive" | "outline";
  }
> = {
  PENDING: { label: "Pendiente", variant: "outline" },
  APPROVED: { label: "Aprobado", variant: "default" },
  CHANGES_REQUESTED: { label: "Cambios solicitados", variant: "destructive" },
  DRAFT: { label: "Borrador", variant: "secondary" },
  SENT: { label: "Enviada", variant: "outline" },
  PAID: { label: "Pagada", variant: "default" },
  ACTIVE: { label: "Activo", variant: "default" },
  COMPLETED: { label: "Completado", variant: "secondary" },
};

export function StatusBadge({ status }: { status: Status }) {
  const config = statusConfig[status];
  return <Badge variant={config.variant}>{config.label}</Badge>;
}
