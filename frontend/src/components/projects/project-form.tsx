"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useCreateProject } from "@/hooks/use-projects";
import { useOrganizations } from "@/hooks/use-organizations";
import {
  createProjectSchema,
  CreateProjectFormData,
} from "@/lib/validators/project.schema";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface ProjectFormProps {
  defaultOrgId?: string;
}

export function ProjectForm({ defaultOrgId }: ProjectFormProps) {
  const router = useRouter();
  const createProject = useCreateProject();
  const { data: organizations, isLoading: orgsLoading } = useOrganizations();

  const form = useForm<CreateProjectFormData>({
    resolver: zodResolver(createProjectSchema),
    defaultValues: {
      name: "",
      description: "",
      org_id: defaultOrgId ?? "",
    },
  });

  function onSubmit(data: CreateProjectFormData) {
    createProject.mutate(data, {
      onSuccess: (project) => {
        router.push(`/projects/${project.id}`);
      },
    });
  }

  if (orgsLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="org_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-zinc-300">Organización</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger className="bg-zinc-900/50 border-zinc-800 text-white">
                    <SelectValue placeholder="Selecciona una organización" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent className="border-white/[0.06] bg-zinc-900">
                  {organizations?.map((org) => (
                    <SelectItem key={org.id} value={org.id}>
                      {org.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-zinc-300">Nombre del proyecto</FormLabel>
              <FormControl>
                <Input
                  placeholder="Rediseño web Q1"
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
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-zinc-300">Descripción</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Descripción opcional del proyecto..."
                  className="resize-none bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600"
                  rows={3}
                  {...field}
                />
              </FormControl>
              <FormDescription className="text-zinc-500">Opcional</FormDescription>
              <FormMessage className="text-red-400" />
            </FormItem>
          )}
        />
        <div className="flex gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            className="border-white/[0.06] hover:bg-white/[0.04]"
            onClick={() => router.back()}
          >
            Cancelar
          </Button>
          <Button type="submit" className="bg-green-500 text-black hover:bg-green-400" disabled={createProject.isPending}>
            {createProject.isPending ? "Creando..." : "Crear proyecto"}
          </Button>
        </div>
      </form>
    </Form>
  );
}
