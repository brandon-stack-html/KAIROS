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
      <DialogContent className="sm:max-w-md border-white/[0.06] bg-zinc-950">
        <DialogHeader>
          <DialogTitle className="text-white">Cambiar rol</DialogTitle>
          <DialogDescription className="text-zinc-400">
            Cambia el rol del miembro{" "}
            <span className="font-mono text-xs text-zinc-300">
              {member.user_id.slice(0, 8)}…
            </span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 py-4">
          <Label className="text-zinc-300">Nuevo rol</Label>
          <Select
            value={selectedRole}
            onValueChange={(v) => setSelectedRole(v as Role)}
          >
            <SelectTrigger className="bg-zinc-900/50 border-zinc-800 text-white">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="border-white/[0.06] bg-zinc-900">
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
            className="border-white/[0.06] hover:bg-white/[0.04]"
            onClick={() => onOpenChange(false)}
            disabled={changeMemberRole.isPending}
          >
            Cancelar
          </Button>
          <Button
            className="bg-green-500 text-black hover:bg-green-400"
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
