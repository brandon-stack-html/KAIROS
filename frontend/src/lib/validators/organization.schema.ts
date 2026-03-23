import { z } from "zod";
import { Role } from "@/types/auth.types";

export const createOrganizationSchema = z.object({
  name: z.string().min(2, "Mínimo 2 caracteres").max(100, "Máximo 100"),
  slug: z
    .string()
    .min(2, "Mínimo 2 caracteres")
    .max(63, "Máximo 63 caracteres")
    .regex(
      /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/,
      "Solo minúsculas, números y guiones"
    ),
});

export const inviteMemberSchema = z.object({
  email: z.string().email("Email inválido"),
  role: z.nativeEnum(Role, { error: "Rol requerido" }),
});

export type CreateOrganizationFormData = z.infer<typeof createOrganizationSchema>;
export type InviteMemberFormData = z.infer<typeof inviteMemberSchema>;
