"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, UserMinus, Shield } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Membership } from "@/types/organization.types";
import { Role } from "@/types/auth.types";
import { ROLE_LABELS } from "@/constants/roles";
import { useRemoveMember } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { RoleGate, getUserRoleInOrg } from "@/components/shared/role-gate";
import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { ChangeRoleDialog } from "./change-role-dialog";
import { format } from "date-fns";
import { es } from "date-fns/locale";

interface MemberTableProps {
  orgId: string;
  members: Membership[];
}

export function MemberTable({ orgId, members }: MemberTableProps) {
  const { user } = useAuthStore();
  const currentUserRole = user ? getUserRoleInOrg(user.id, members) : undefined;
  const removeMember = useRemoveMember(orgId);

  const [removeTarget, setRemoveTarget] = useState<string | null>(null);
  const [roleTarget, setRoleTarget] = useState<Membership | null>(null);

  return (
    <>
      <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Usuario</TableHead>
            <TableHead>Rol</TableHead>
            <TableHead>Fecha de ingreso</TableHead>
            <TableHead className="w-12" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {members.map((member) => {
            const isCurrentUser = member.user_id === user?.id;
            const isOwner = member.role === Role.OWNER;

            return (
              <TableRow key={member.user_id}>
                <TableCell className="font-mono text-sm">
                  {member.user_id.slice(0, 8)}…
                  {isCurrentUser && (
                    <Badge variant="outline" className="ml-2 text-xs">
                      Tú
                    </Badge>
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant="secondary">
                    {ROLE_LABELS[member.role]}
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {format(new Date(member.joined_at), "d MMM yyyy", {
                    locale: es,
                  })}
                </TableCell>
                <TableCell>
                  {!isCurrentUser && !isOwner && (
                    <RoleGate
                      allowedRoles={[Role.OWNER, Role.ADMIN]}
                      userRole={currentUserRole}
                    >
                      <DropdownMenu>
                        <DropdownMenuTrigger
                          render={
                            <Button variant="ghost" size="icon" className="size-8" />
                          }
                        >
                          <MoreHorizontal className="size-4" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <RoleGate
                            allowedRoles={[Role.OWNER]}
                            userRole={currentUserRole}
                          >
                            <DropdownMenuItem
                              onClick={() => setRoleTarget(member)}
                            >
                              <Shield className="mr-2 size-4" />
                              Cambiar rol
                            </DropdownMenuItem>
                          </RoleGate>
                          <DropdownMenuItem
                            onClick={() => setRemoveTarget(member.user_id)}
                            className="text-destructive focus:text-destructive"
                          >
                            <UserMinus className="mr-2 size-4" />
                            Eliminar miembro
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </RoleGate>
                  )}
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      </div>

      <ConfirmDialog
        open={!!removeTarget}
        onOpenChange={(open) => !open && setRemoveTarget(null)}
        title="Eliminar miembro"
        description="¿Estás seguro de que deseas eliminar a este miembro de la organización? Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
        isLoading={removeMember.isPending}
        onConfirm={() => {
          if (removeTarget) {
            removeMember.mutate(removeTarget, {
              onSuccess: () => setRemoveTarget(null),
            });
          }
        }}
      />

      {roleTarget && (
        <ChangeRoleDialog
          orgId={orgId}
          member={roleTarget}
          open={!!roleTarget}
          onOpenChange={(open) => !open && setRoleTarget(null)}
        />
      )}
    </>
  );
}
