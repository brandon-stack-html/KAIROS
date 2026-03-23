"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Membership } from "@/types/organization.types";
import { Role } from "@/types/auth.types";
import { ROLE_LABELS } from "@/constants/roles";
import { useChangeMemberRole } from "@/hooks/use-organizations";

interface ChangeRoleDialogProps {
  orgId: string;
  member: Membership;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ChangeRoleDialog({
  orgId,
  member,
  open,
  onOpenChange,
}: ChangeRoleDialogProps) {
  const [selectedRole, setSelectedRole] = useState<Role>(member.role);
  const changeMemberRole = useChangeMemberRole(orgId);

  function handleSave() {
    if (selectedRole === member.role) {
      onOpenChange(false);
      return;
    }
    changeMemberRole.mutate(
      { userId: member.user_id, data: { role: selectedRole } },
      { onSuccess: () => onOpenChange(false) }
    );
  }

  const assignableRoles = [Role.ADMIN, Role.MEMBER];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Cambiar rol</DialogTitle>
          <DialogDescription>
            Cambia el rol del miembro{" "}
            <span className="font-mono text-xs">
              {member.user_id.slice(0, 8)}…
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-4">
          <Label>Nuevo rol</Label>
          <Select
            value={selectedRole}
            onValueChange={(v) => setSelectedRole(v as Role)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {assignableRoles.map((role) => (
                <SelectItem key={role} value={role}>
                  {ROLE_LABELS[role]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={changeMemberRole.isPending}
          >
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
            disabled={changeMemberRole.isPending}
          >
            {changeMemberRole.isPending ? "Guardando..." : "Guardar"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
