"use client";

import { DeliverableStatus } from "@/types/deliverable.types";
import { InvoiceStatus } from "@/types/invoice.types";
import { ProjectStatus } from "@/types/project.types";

type Status = DeliverableStatus | InvoiceStatus | ProjectStatus;

const statusConfig: Record<
  Status,
  {
    label: string;
    className: string;
  }
> = {
  PENDING: {
    label: "Pendiente",
    className:
      "bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  APPROVED: {
    label: "Aprobado",
    className:
      "bg-green-500/10 text-green-400 border border-green-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  CHANGES_REQUESTED: {
    label: "Cambios solicitados",
    className:
      "bg-red-500/10 text-red-400 border border-red-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  DRAFT: {
    label: "Borrador",
    className:
      "bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  SENT: {
    label: "Enviada",
    className:
      "bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  PAID: {
    label: "Pagada",
    className:
      "bg-zinc-600/10 text-zinc-400 border border-zinc-600/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  ACTIVE: {
    label: "Activo",
    className:
      "bg-green-500/10 text-green-400 border border-green-500/20 rounded-full px-2 py-1 text-xs font-medium",
  },
  COMPLETED: {
    label: "Completado",
    className:
      "bg-zinc-600/10 text-zinc-400 border border-zinc-600/20 rounded-full px-2 py-1 text-xs font-medium",
  },
};

export function StatusBadge({ status }: { status: Status }) {
  const config = statusConfig[status];
  return <span className={config.className}>{config.label}</span>;
}
