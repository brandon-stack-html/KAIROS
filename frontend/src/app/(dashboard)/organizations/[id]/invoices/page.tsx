"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useInvoices } from "@/hooks/use-invoices";
import { useOrganization } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { getUserRoleInOrg } from "@/components/shared/role-gate";
import { RoleGate } from "@/components/shared/role-gate";
import { InvoiceTable } from "@/components/invoices/invoice-table";
import { InvoiceForm } from "@/components/invoices/invoice-form";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, ArrowLeft } from "lucide-react";
import { Role } from "@/types/auth.types";
import { InvoiceStatus } from "@/types/invoice.types";

export default function OrganizationInvoicesPage() {
  const { id } = useParams<{ id: string }>();
  const { data: invoices, isLoading: invoicesLoading } = useInvoices(id);
  const { data: org } = useOrganization(id);
  const { user } = useAuthStore();
  const [formOpen, setFormOpen] = useState(false);

  const userRole =
    user && org ? getUserRoleInOrg(user.id, org.members) : undefined;

  const totalAmount =
    invoices?.reduce((sum, inv) => sum + parseFloat(inv.amount), 0) ?? 0;
  const paidAmount =
    invoices
      ?.filter((inv) => inv.status === InvoiceStatus.PAID)
      .reduce((sum, inv) => sum + parseFloat(inv.amount), 0) ?? 0;
  const pendingAmount = totalAmount - paidAmount;

  function formatCurrency(amount: number): string {
    return new Intl.NumberFormat("es-CO", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(amount);
  }

  if (invoicesLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="text-zinc-400 hover:text-zinc-200" nativeButton={false} render={<Link href={`/organizations/${id}`} />}>
            <ArrowLeft className="size-4" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Facturas</h1>
            {org && (
              <p className="text-sm text-zinc-500">{org.name}</p>
            )}
          </div>
        </div>
        <RoleGate
          allowedRoles={[Role.OWNER, Role.ADMIN]}
          userRole={userRole}
        >
          <Button className="bg-green-500 text-black hover:bg-green-400" onClick={() => setFormOpen(true)}>
            <Plus className="mr-2 size-4" />
            Nueva factura
          </Button>
        </RoleGate>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-white/[0.06]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">
              Total facturado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold font-mono text-white">{formatCurrency(totalAmount)}</p>
          </CardContent>
        </Card>
        <Card className="border-white/[0.06]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">
              Pagado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold font-mono text-green-400">
              {formatCurrency(paidAmount)}
            </p>
          </CardContent>
        </Card>
        <Card className="border-white/[0.06]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-500">
              Pendiente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold font-mono text-amber-400">
              {formatCurrency(pendingAmount)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabla de facturas */}
      <Card className="border-white/[0.06]">
        <CardContent className="pt-6">
          <InvoiceTable
            orgId={id}
            invoices={invoices ?? []}
            userRole={userRole}
          />
        </CardContent>
      </Card>

      {/* Form dialog */}
      <InvoiceForm orgId={id} open={formOpen} onOpenChange={setFormOpen} />
    </div>
  );
}
