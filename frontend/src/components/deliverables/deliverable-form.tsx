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
      <DialogContent className="sm:max-w-md border-white/[0.06] bg-zinc-950">
        <DialogHeader>
          <DialogTitle className="text-white">Enviar entregable</DialogTitle>
          <DialogDescription className="text-zinc-400">
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
                  <FormLabel className="text-zinc-300">Título</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Diseño de landing page v2"
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
              name="url_link"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-zinc-300">URL</FormLabel>
                  <FormControl>
                    <Input
                      type="url"
                      placeholder="https://figma.com/file/..."
                      className="bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600"
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
                disabled={submitDeliverable.isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" className="bg-green-500 text-black hover:bg-green-400" disabled={submitDeliverable.isPending}>
                {submitDeliverable.isPending ? "Enviando..." : "Enviar"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
