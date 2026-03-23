"use client";

import { SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { usePathname } from "next/navigation";

const pathLabels: Record<string, string> = {
  "/": "Dashboard",
  "/organizations": "Organizaciones",
  "/organizations/new": "Nueva organización",
  "/projects": "Proyectos",
  "/projects/new": "Nuevo proyecto",
  "/settings": "Configuración",
};

export function Header() {
  const pathname = usePathname();
  const label = pathLabels[pathname] ?? "Kairos";

  return (
    <header className="flex h-14 items-center gap-3 border-b bg-background px-4">
      <SidebarTrigger />
      <Separator orientation="vertical" className="h-5" />
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbPage>{label}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
    </header>
  );
}
