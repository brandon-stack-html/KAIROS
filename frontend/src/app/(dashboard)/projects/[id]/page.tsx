"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useProject } from "@/hooks/use-projects";
import { useOrganization } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { getUserRoleInOrg } from "@/components/shared/role-gate";
import { StatusBadge } from "@/components/shared/status-badge";
import { DeliverableList } from "@/components/deliverables/deliverable-list";
import { ProjectSummary } from "@/components/projects/project-summary";
import { ChatPanel } from "@/components/chat/chat-panel";
import { DocumentList } from "@/components/documents/document-list";
import {
  useProjectDocuments,
  useUploadProjectDocument,
  useDeleteDocument,
} from "@/hooks/use-documents";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ClipboardList, FolderOpen, MessageSquare, Sparkles } from "lucide-react";

type Tab = "deliverables" | "chat" | "summary" | "documents";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: project, isLoading: projectLoading } = useProject(id);
  const { data: org } = useOrganization(project?.org_id ?? "");
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<Tab>("deliverables");

  const userRole =
    user && org ? getUserRoleInOrg(user.id, org.members) : undefined;
  const { data: documents = [] } = useProjectDocuments(id);
  const uploadDoc = useUploadProjectDocument(id, project?.org_id ?? "");
  const deleteDoc = useDeleteDocument(project?.org_id, id);

  if (projectLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-96" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!project) {
    return (
      <p className="text-zinc-500">Proyecto no encontrado.</p>
    );
  }

  const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: "deliverables", label: "Entregables", icon: ClipboardList },
    { key: "chat", label: "Chat", icon: MessageSquare },
    { key: "summary", label: "AI Summary", icon: Sparkles },
    { key: "documents", label: "Documentos", icon: FolderOpen },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold tracking-tight">
              {project.name}
            </h1>
            {project.description && (
              <p className="text-sm text-zinc-400 max-w-2xl">
                {project.description}
              </p>
            )}
            {org && (
              <div className="flex items-center gap-2 pt-1">
                <Badge variant="outline" className="border-white/[0.06] bg-white/[0.02] text-zinc-300">{org.name}</Badge>
              </div>
            )}
          </div>
          <StatusBadge status={project.status} />
        </div>
      </div>

      {/* Tabs */}
      <nav className="flex gap-1 border-b border-white/[0.06]" role="tablist">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            role="tab"
            aria-selected={activeTab === key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
              activeTab === key
                ? "border-green-500 text-white"
                : "border-transparent text-zinc-500 hover:text-zinc-200"
            }`}
          >
            <Icon className="size-4" />
            {label}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      {activeTab === "deliverables" && (
        <DeliverableList projectId={id} userRole={userRole} />
      )}

      {activeTab === "chat" && (
        <ChatPanel orgId={project.org_id} projectId={id} />
      )}

      {activeTab === "summary" && <ProjectSummary projectId={id} />}

      {activeTab === "documents" && (
        <DocumentList
          documents={documents}
          onUpload={(file) => uploadDoc.mutate(file)}
          onDelete={(docId) => deleteDoc.mutate(docId)}
          isPendingUpload={uploadDoc.isPending}
          currentUserId={user?.id}
        />
      )}
    </div>
  );
}
