import { z } from "zod";

export const createDeliverableSchema = z.object({
  title: z.string().min(2, "Mínimo 2 caracteres").max(100, "Máximo 100"),
  url_link: z.string().url("URL inválida").max(2048, "URL demasiado larga"),
});

export type CreateDeliverableFormData = z.infer<typeof createDeliverableSchema>;
