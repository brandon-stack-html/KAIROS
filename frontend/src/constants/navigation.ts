import {
  LayoutDashboard,
  Building2,
  FolderKanban,
  Settings,
} from "lucide-react";

export const navigation = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Organizaciones", href: "/organizations", icon: Building2 },
  { label: "Proyectos", href: "/projects", icon: FolderKanban },
  { label: "Configuración", href: "/settings", icon: Settings },
];
