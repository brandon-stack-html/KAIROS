"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Role } from "@/types/auth.types";
import { ROLE_LABELS } from "@/constants/roles";
import {
  inviteMemberSchema,
  InviteMemberFormData,
} from "@/lib/validators/organization.schema";
import { useInviteMember } from "@/hooks/use-organizations";

interface InviteMemberDialogProps {
  orgId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InviteMemberDialog({
  orgId,
  open,
  onOpenChange,
}: InviteMemberDialogProps) {
  const inviteMember = useInviteMember(orgId);

  const form = useForm<InviteMemberFormData>({
    resolver: zodResolver(inviteMemberSchema),
    defaultValues: { email: "", role: Role.MEMBER },
  });

  function onSubmit(data: InviteMemberFormData) {
    inviteMember.mutate(
      { email: data.email, role: data.role },
      {
        onSuccess: () => {
          form.reset();
          onOpenChange(false);
        },
      }
    );
  }

  const invitableRoles = [Role.ADMIN, Role.MEMBER];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md border-white/[0.06] bg-zinc-950">
        <DialogHeader>
          <DialogTitle className="text-white">Invitar miembro</DialogTitle>
          <DialogDescription className="text-zinc-400">
            Envía una invitación por email para unirse a la organización
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-zinc-300">Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="colega@email.com"
                      className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="role"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-zinc-300">Rol</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                  >
                    <FormControl>
                      <SelectTrigger className="bg-zinc-900/50 border-zinc-800 text-white">
                        <SelectValue placeholder="Selecciona un rol" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="border-white/[0.06] bg-zinc-900">
                      {invitableRoles.map((role) => (
                        <SelectItem key={role} value={role}>
                          {ROLE_LABELS[role]}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />

            <DialogFooter className="pt-2">
              <Button
                type="button"
                variant="outline"
                className="border-white/[0.06] hover:bg-white/[0.04]"
                onClick={() => onOpenChange(false)}
                disabled={inviteMember.isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" className="bg-green-500 text-black hover:bg-green-400" disabled={inviteMember.isPending}>
                {inviteMember.isPending ? "Enviando..." : "Enviar invitación"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
