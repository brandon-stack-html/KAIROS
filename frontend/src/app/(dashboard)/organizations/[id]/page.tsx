"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useOrganization } from "@/hooks/use-organizations";
import { useAuthStore } from "@/stores/auth.store";
import { MemberTable } from "@/components/organizations/member-table";
import { InviteMemberDialog } from "@/components/organizations/invite-member-dialog";
import { RoleGate, getUserRoleInOrg } from "@/components/shared/role-gate";
import { ChatPanel } from "@/components/chat/chat-panel";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DocumentList } from "@/components/documents/document-list";
import {
  useOrgDocuments,
  useUploadOrgDocument,
  useDeleteDocument,
} from "@/hooks/use-documents";
import { UserPlus, FileText, Users, MessageSquare, FolderOpen } from "lucide-react";
import { Role } from "@/types/auth.types";

type Tab = "members" | "invoices" | "chat" | "documents";

export default function OrganizationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: org, isLoading } = useOrganization(id);
  const { user } = useAuthStore();
  const [inviteOpen, setInviteOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("members");

  const currentUserRole =
    user && org ? getUserRoleInOrg(user.id, org.members) : undefined;
  const { data: documents = [] } = useOrgDocuments(id);
  const uploadDoc = useUploadOrgDocument(id);
  const deleteDoc = useDeleteDocument(id);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!org) {
    return (
      <p className="text-muted-foreground">Organización no encontrada.</p>
    );
  }

  const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
    { key: "members", label: "Miembros", icon: Users },
    { key: "invoices", label: "Facturas", icon: FileText },
    { key: "chat", label: "Chat", icon: MessageSquare },
    { key: "documents", label: "Documentos", icon: FolderOpen },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{org.name}</h1>
          <Badge variant="secondary" className="mt-1">
            {org.slug}
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === key
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            <Icon className="size-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "members" && (
        <>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-lg">
                Miembros ({org.members.length})
              </CardTitle>
              <RoleGate
                allowedRoles={[Role.OWNER, Role.ADMIN]}
                userRole={currentUserRole}
              >
                <Button size="sm" onClick={() => setInviteOpen(true)}>
                  <UserPlus className="mr-2 size-4" />
                  Invitar
                </Button>
              </RoleGate>
            </CardHeader>
            <CardContent>
              <MemberTable orgId={id} members={org.members} />
            </CardContent>
          </Card>

          <InviteMemberDialog
            orgId={id}
            open={inviteOpen}
            onOpenChange={setInviteOpen}
          />
        </>
      )}

      {activeTab === "invoices" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Facturas</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-muted-foreground">
              Gestiona las facturas de esta organización.
            </p>
            <Button variant="outline" render={<Link href={`/organizations/${id}/invoices`} />}>
              <FileText className="mr-2 size-4" />
              Ver todas las facturas
            </Button>
          </CardContent>
        </Card>
      )}

      {activeTab === "chat" && <ChatPanel orgId={id} />}

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
