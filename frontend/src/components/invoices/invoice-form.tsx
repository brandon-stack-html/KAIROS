"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useCreateInvoice } from "@/hooks/use-invoices";
import {
  createInvoiceSchema,
  CreateInvoiceFormData,
} from "@/lib/validators/invoice.schema";
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
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface InvoiceFormProps {
  orgId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InvoiceForm({ orgId, open, onOpenChange }: InvoiceFormProps) {
  const createInvoice = useCreateInvoice(orgId);

  const form = useForm<CreateInvoiceFormData>({
    resolver: zodResolver(createInvoiceSchema),
    defaultValues: { title: "", amount: "" },
  });

  function onSubmit(data: CreateInvoiceFormData) {
    createInvoice.mutate(
      { title: data.title, amount: data.amount },
      {
        onSuccess: () => {
          form.reset();
          onOpenChange(false);
        },
      }
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md border-white/[0.06] bg-zinc-950">
        <DialogHeader>
          <DialogTitle className="text-white">Nueva factura</DialogTitle>
          <DialogDescription className="text-zinc-400">
            Crea una factura para esta organización
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-zinc-300">Título</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Desarrollo web - Marzo 2026"
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
              name="amount"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-zinc-300">Monto (USD)</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="2500.00"
                      inputMode="decimal"
                      className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 font-mono"
                      {...field}
                    />
                  </FormControl>
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
                disabled={createInvoice.isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" className="bg-green-500 text-black hover:bg-green-400" disabled={createInvoice.isPending}>
                {createInvoice.isPending ? "Creando..." : "Crear factura"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
