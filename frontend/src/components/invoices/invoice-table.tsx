"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import { RoleGate } from "@/components/shared/role-gate";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { Invoice, InvoiceStatus } from "@/types/invoice.types";
import { Role } from "@/types/auth.types";
import { useMarkInvoicePaid } from "@/hooks/use-invoices";
import { CircleDollarSign } from "lucide-react";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { useState } from "react";

interface InvoiceTableProps {
  orgId: string;
  invoices: Invoice[];
  userRole: Role | undefined;
}

function formatAmount(amount: string): string {
  const num = parseFloat(amount);
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(num);
}

export function InvoiceTable({ orgId, invoices, userRole }: InvoiceTableProps) {
  const markPaid = useMarkInvoicePaid(orgId);
  const [payTarget, setPayTarget] = useState<string | null>(null);

  return (
    <>
      <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow className="border-white/[0.06]">
            <TableHead className="text-zinc-500">Título</TableHead>
            <TableHead className="text-right text-zinc-500">Monto</TableHead>
            <TableHead className="text-zinc-500">Estado</TableHead>
            <TableHead className="text-zinc-500">Creada</TableHead>
            <TableHead className="text-zinc-500">Pagada</TableHead>
            <TableHead className="w-12 text-zinc-500" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {invoices.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-zinc-500 py-8">
                No hay facturas aún
              </TableCell>
            </TableRow>
          ) : (
            invoices.map((invoice) => (
              <TableRow key={invoice.id} className="border-white/[0.06] hover:bg-white/[0.02] transition-colors">
                <TableCell className="font-medium text-white">
                  {invoice.title}
                </TableCell>
                <TableCell className="text-right font-mono text-white">
                  {formatAmount(invoice.amount)}
                </TableCell>
                <TableCell>
                  <StatusBadge status={invoice.status} />
                </TableCell>
                <TableCell className="text-zinc-500 text-sm font-mono">
                  {format(new Date(invoice.created_at), "d MMM yyyy", {
                    locale: es,
                  })}
                </TableCell>
                <TableCell className="text-zinc-500 text-sm font-mono">
                  {invoice.paid_at
                    ? format(new Date(invoice.paid_at), "d MMM yyyy", {
                        locale: es,
                      })
                    : "—"}
                </TableCell>
                <TableCell>
                  {invoice.status !== InvoiceStatus.PAID && (
                    <RoleGate
                      allowedRoles={[Role.OWNER, Role.ADMIN]}
                      userRole={userRole}
                    >
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-green-500/20 hover:border-green-500/40 hover:bg-green-500/10 text-green-400"
                        onClick={() => setPayTarget(invoice.id)}
                      >
                        <CircleDollarSign className="mr-1.5 size-3.5" />
                        Pagada
                      </Button>
                    </RoleGate>
                  )}
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </div>

      <ConfirmDialog
        open={!!payTarget}
        onOpenChange={(open) => !open && setPayTarget(null)}
        title="Marcar como pagada"
        description="¿Confirmas que esta factura ha sido pagada? Esta acción no se puede deshacer."
        confirmLabel="Confirmar pago"
        isLoading={markPaid.isPending}
        onConfirm={() => {
          if (payTarget) {
            markPaid.mutate(payTarget, {
              onSuccess: () => setPayTarget(null),
            });
          }
        }}
      />
    </>
  );
}
