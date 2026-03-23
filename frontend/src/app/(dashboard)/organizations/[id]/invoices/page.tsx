"use client";

import { useParams } from "next/navigation";

export default function OrganizationInvoicesPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h1 className="text-2xl font-bold tracking-tight">Facturas</h1>
      <p className="text-muted-foreground mt-1">
        Sprint 4 — Org: {id.slice(0, 8)}…
      </p>
    </div>
  );
}
