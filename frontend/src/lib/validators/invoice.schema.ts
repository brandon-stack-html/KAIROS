import { z } from "zod";

export const createInvoiceSchema = z.object({
  title: z.string().min(1, "Título requerido").max(200, "Máximo 200 caracteres"),
  amount: z
    .string()
    .min(1, "Monto requerido")
    .regex(/^\d+(\.\d{1,2})?$/, "Formato: 1234.56 (máximo 2 decimales)")
    .refine((val) => parseFloat(val) > 0, "Debe ser mayor a 0"),
});

export type CreateInvoiceFormData = z.infer<typeof createInvoiceSchema>;
