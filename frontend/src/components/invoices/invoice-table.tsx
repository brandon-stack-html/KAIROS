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
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Título</TableHead>
            <TableHead className="text-right">Monto</TableHead>
            <TableHead>Estado</TableHead>
            <TableHead>Creada</TableHead>
            <TableHead>Pagada</TableHead>
            <TableHead className="w-12" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {invoices.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                No hay facturas aún
              </TableCell>
            </TableRow>
          ) : (
            invoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell className="font-medium">
                  {invoice.title}
                </TableCell>
                <TableCell className="text-right font-mono">
                  {formatAmount(invoice.amount)}
                </TableCell>
                <TableCell>
                  <StatusBadge status={invoice.status} />
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
                  {format(new Date(invoice.created_at), "d MMM yyyy", {
                    locale: es,
                  })}
                </TableCell>
                <TableCell className="text-muted-foreground text-sm">
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
