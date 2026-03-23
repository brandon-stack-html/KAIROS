"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useCreateOrganization } from "@/hooks/use-organizations";
import {
  createOrganizationSchema,
  CreateOrganizationFormData,
} from "@/lib/validators/organization.schema";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function OrganizationForm() {
  const router = useRouter();
  const createOrg = useCreateOrganization();

  const form = useForm<CreateOrganizationFormData>({
    resolver: zodResolver(createOrganizationSchema),
    defaultValues: { name: "", slug: "" },
  });

  function handleNameChange(value: string, onChange: (v: string) => void) {
    onChange(value);
    const slug = value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 63);
    form.setValue("slug", slug, { shouldValidate: true });
  }

  function onSubmit(data: CreateOrganizationFormData) {
    createOrg.mutate(data, {
      onSuccess: (org) => {
        router.push(`/organizations/${org.id}`);
      },
    });
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nombre</FormLabel>
              <FormControl>
                <Input
                  placeholder="Mi Empresa"
                  {...field}
                  onChange={(e) =>
                    handleNameChange(e.target.value, field.onChange)
                  }
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="slug"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Slug</FormLabel>
              <FormControl>
                <Input placeholder="mi-empresa" {...field} />
              </FormControl>
              <FormDescription>
                Identificador único. Solo minúsculas, números y guiones.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
          >
            Cancelar
          </Button>
          <Button type="submit" disabled={createOrg.isPending}>
            {createOrg.isPending ? "Creando..." : "Crear organización"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
