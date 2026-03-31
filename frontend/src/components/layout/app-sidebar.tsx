"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LogOut, ChevronsUpDown, Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { navigation } from "@/constants/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { useLogout } from "@/hooks/use-auth";

export function AppSidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const logoutMutation = useLogout();

  const initials =
    user?.name
      ?.split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2) ?? "?";

  return (
    <Sidebar className="border-r border-white/[0.06]">
      <SidebarHeader className="border-b border-white/[0.06] px-4 py-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-green-500 text-black">
            <Zap className="w-4 h-4 font-bold" />
          </div>
          <span className="text-xl font-bold tracking-tighter">Kairos</span>
        </Link>
      </SidebarHeader>

      <SidebarContent className="px-2 py-4">
        <SidebarMenu>
          {navigation.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <SidebarMenuItem key={item.href}>
                <SidebarMenuButton
                  isActive={isActive}
                  render={<Link href={item.href} />}
                  className={cn(
                    "text-sm text-zinc-400 hover:text-zinc-200 transition-colors duration-150",
                    isActive && "border-l-2 border-green-500 bg-white/[0.04] text-white"
                  )}
                >
                  <item.icon className="size-4 text-zinc-500" />
                  <span>{item.label}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="border-t border-white/[0.06] p-2">
        <DropdownMenu>
          <DropdownMenuTrigger
              render={
                <button className="flex w-full items-center gap-3 rounded-lg p-2 text-left text-sm hover:bg-white/[0.04] transition-colors duration-150" />
              }
            >
              <Avatar className="size-8 ring-2 ring-white/[0.06]">
                <AvatarFallback className="text-xs font-medium">{initials}</AvatarFallback>
              </Avatar>
              <div className="flex-1 truncate">
                <p className="truncate text-sm font-medium text-white">{user?.name}</p>
                <p className="truncate text-xs text-zinc-500">
                  {user?.email}
                </p>
              </div>
              <ChevronsUpDown className="size-4 text-zinc-500" />
            </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56 border-white/[0.06] bg-zinc-900">
            <DropdownMenuItem
              onClick={() => logoutMutation.mutate()}
              className="text-red-400 focus:text-red-300 focus:bg-red-500/10 cursor-pointer"
            >
              <LogOut className="mr-2 size-4" />
              Cerrar sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
