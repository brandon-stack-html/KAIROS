"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useOrganization } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { MemberTable } from "@/components/organizations/member-table";
import { InviteMemberDialog } from "@/components/organizations/invite-member-dialog";
import { RoleGate, getUserRoleInOrg } from "@/components/shared/role-gate";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserPlus, FileText } from "lucide-react";
import { Role } from "@/types/auth.types";

export default function OrganizationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: org, isLoading } = useOrganization(id);
  const { user } = useAuthStore();
  const [inviteOpen, setInviteOpen] = useState(false);

  const currentUserRole =
    user && org ? getUserRoleInOrg(user.id, org.members) : undefined;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!org) {
    return (
      <p className="text-muted-foreground">Organización no encontrada.</p>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{org.name}</h1>
          <Badge variant="secondary" className="mt-1">
            {org.slug}
          </Badge>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" render={<Link href={`/organizations/${id}/invoices`} />}>
            <FileText className="mr-2 size-4" />
            Facturas
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-lg">
            Miembros ({org.members.length})
          </CardTitle>
          <RoleGate
            allowedRoles={[Role.OWNER, Role.ADMIN]}
            userRole={currentUserRole}
          >
            <Button size="sm" onClick={() => setInviteOpen(true)}>
              <UserPlus className="mr-2 size-4" />
              Invitar
            </Button>
          </RoleGate>
        </CardHeader>
        <CardContent>
          <MemberTable orgId={id} members={org.members} />
        </CardContent>
      </Card>

      <InviteMemberDialog
        orgId={id}
        open={inviteOpen}
        onOpenChange={setInviteOpen}
      />
    </div>
  );
}
