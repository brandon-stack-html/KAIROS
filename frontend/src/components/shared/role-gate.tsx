"use client";

import { Role } from "@/types/auth.types";
import { Membership } from "@/types/organization.types";

interface RoleGateProps {
  allowedRoles: Role[];
  userRole: Role | undefined;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGate({
  allowedRoles,
  userRole,
  children,
  fallback,
}: RoleGateProps) {
  if (!userRole || !allowedRoles.includes(userRole)) {
    return fallback ?? null;
  }
  return <>{children}</>;
}

export function getUserRoleInOrg(
  userId: string,
  members: Membership[]
): Role | undefined {
  return members.find((m) => m.user_id === userId)?.role;
}
