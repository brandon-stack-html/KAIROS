"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSubmitDeliverable } from "@/hooks/use-deliverables";
import {
  createDeliverableSchema,
  CreateDeliverableFormData,
} from "@/lib/validators/deliverable.schema";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface DeliverableFormProps {
  projectId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DeliverableForm({
  projectId,
  open,
  onOpenChange,
}: DeliverableFormProps) {
  const submitDeliverable = useSubmitDeliverable(projectId);

  const form = useForm<CreateDeliverableFormData>({
    resolver: zodResolver(createDeliverableSchema),
    defaultValues: { title: "", url_link: "" },
  });

  function onSubmit(data: CreateDeliverableFormData) {
    submitDeliverable.mutate(data, {
      onSuccess: () => {
        form.reset();
        onOpenChange(false);
      },
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Enviar entregable</DialogTitle>
          <DialogDescription>
            Comparte un enlace al trabajo realizado
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Título</FormLabel>
                  <FormControl>
                    <Input placeholder="Diseño de landing page v2" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="url_link"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>URL</FormLabel>
                  <FormControl>
                    <Input
                      type="url"
                      placeholder="https://figma.com/file/..."
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter className="pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={submitDeliverable.isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={submitDeliverable.isPending}>
                {submitDeliverable.isPending ? "Enviando..." : "Enviar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
