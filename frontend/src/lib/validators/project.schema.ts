import { z } from "zod";

export const createProjectSchema = z.object({
  name: z.string().min(2, "Mínimo 2 caracteres").max(100, "Máximo 100"),
  description: z.string(),
  org_id: z.string().uuid("Organización requerida"),
});

export type CreateProjectFormData = z.infer<typeof createProjectSchema>;
