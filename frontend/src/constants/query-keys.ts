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
  conversations: {
    all: ["conversations"] as const,
    byOrg: (orgId: string) =>
      [...queryKeys.conversations.all, "org", orgId] as const,
    detail: (id: string) =>
      [...queryKeys.conversations.all, id] as const,
    messages: (conversationId: string) =>
      [...queryKeys.conversations.all, conversationId, "messages"] as const,
  },
  documents: {
    all: ["documents"] as const,
    byOrg: (orgId: string) =>
      [...queryKeys.documents.all, "org", orgId] as const,
    byProject: (projectId: string) =>
      [...queryKeys.documents.all, "project", projectId] as const,
  },
  users: {
    me: ["users", "me"] as const,
  },
  dashboard: {
    stats: ["dashboard", "stats"] as const,
  },
};
