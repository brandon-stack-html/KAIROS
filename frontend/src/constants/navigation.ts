import {
  LayoutDashboard,
  Building2,
  FolderKanban,
  MessageSquare,
  Settings,
} from "lucide-react";

export const navigation = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Organizaciones", href: "/organizations", icon: Building2 },
  { label: "Proyectos", href: "/projects", icon: FolderKanban },
  { label: "Mensajes", href: "/messages", icon: MessageSquare },
  { label: "Configuración", href: "/settings", icon: Settings },
];
