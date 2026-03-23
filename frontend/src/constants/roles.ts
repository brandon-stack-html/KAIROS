import { Role } from "@/types/auth.types";

export const ROLE_LABELS: Record<Role, string> = {
  [Role.OWNER]: "Propietario",
  [Role.ADMIN]: "Administrador",
  [Role.MEMBER]: "Miembro",
};

export const ROLE_HIERARCHY: Record<Role, number> = {
  [Role.OWNER]: 3,
  [Role.ADMIN]: 2,
  [Role.MEMBER]: 1,
};
