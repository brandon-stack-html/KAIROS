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
    <header className="sticky top-0 z-50 flex h-14 items-center gap-3 border-b bg-background/80 backdrop-blur-md px-4">
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
