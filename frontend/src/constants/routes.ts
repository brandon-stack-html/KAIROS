export const ROUTES = {
  SELECT_WORKSPACE: "/select-workspace",
  LOGIN: "/login",
  REGISTER: "/register",
  DASHBOARD: "/",
  ORGANIZATIONS: "/organizations",
  PROJECTS: "/projects",
  MESSAGES: "/messages",
  SETTINGS: "/settings",
  ACCEPT_INVITATION: "/accept-invitation",
} as const;

export const PUBLIC_ROUTES = [
  ROUTES.SELECT_WORKSPACE,
  ROUTES.LOGIN,
  ROUTES.REGISTER,
];
