export const queryKeys = {
  organizations: {
    all: ["organizations"] as const,
    list: () => [...queryKeys.organizations.all, "list"] as const,
    detail: (id: string) => [...queryKeys.organizations.all, id] as const,
  },
  projects: {
    all: ["projects"] as const,
    list: (orgId?: string) =>
      [...queryKeys.projects.all, "list", orgId] as const,
    detail: (id: string) => [...queryKeys.projects.all, id] as const,
    summary: (id: string) =>
      [...queryKeys.projects.all, id, "summary"] as const,
  },
  deliverables: {
    all: ["deliverables"] as const,
    byProject: (projectId: string) =>
      [...queryKeys.deliverables.all, "project", projectId] as const,
  },
  invoices: {
    all: ["invoices"] as const,
    byOrg: (orgId: string) =>
      [...queryKeys.invoices.all, "org", orgId] as const,
  },
  users: {
    me: ["users", "me"] as const,
  },
};
