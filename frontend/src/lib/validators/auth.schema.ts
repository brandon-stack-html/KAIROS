import { z } from "zod";

export const workspaceSchema = z.object({
  slug: z
    .string()
    .min(2, "Mínimo 2 caracteres")
    .max(63, "Máximo 63 caracteres")
    .regex(
      /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/,
      "Solo minúsculas, números y guiones"
    ),
});

export const loginSchema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(6, "Mínimo 6 caracteres"),
});

export const registerSchema = z
  .object({
    name: z.string().min(2, "Mínimo 2 caracteres").max(100, "Máximo 100"),
    email: z.string().email("Email inválido"),
    password: z.string().min(8, "Mínimo 8 caracteres"),
    confirmPassword: z.string(),
    tenant_id: z.string().uuid("Workspace inválido"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Las contraseñas no coinciden",
    path: ["confirmPassword"],
  });

export type WorkspaceFormData = z.infer<typeof workspaceSchema>;
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
