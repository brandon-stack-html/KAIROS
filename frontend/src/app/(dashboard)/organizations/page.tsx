"use client";

import Link from "next/link";
import { useOrganizations } from "@/hooks/use-organizations";
import { OrganizationCard } from "@/components/organizations/organization-card";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Building2, Plus } from "lucide-react";

export default function OrganizationsPage() {
  const { data: organizations, isLoading } = useOrganizations();

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Organizaciones</h1>
        <Button className="bg-green-500 text-black hover:bg-green-400" nativeButton={false} render={<Link href="/organizations/new" />}>
          <Plus className="mr-2 size-4" />
          Nueva organización
        </Button>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : organizations?.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="Sin organizaciones"
          description="Crea tu primera organización para comenzar a gestionar proyectos y equipo."
          action={
            <Button className="bg-green-500 text-black hover:bg-green-400" nativeButton={false} render={<Link href="/organizations/new" />}>
              <Plus className="mr-2 size-4" />
              Crear organización
            </Button>
          }
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {organizations?.map((org) => (
            <OrganizationCard key={org.id} organization={org} />
          ))}
        </div>
      )}
    </div>
  );
}
