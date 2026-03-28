"use client";

import { useState } from "react";
import { useOrganizations } from "@/hooks/use-organizations";
import {
  useOrgConversations,
  useMessages,
  useSendMessage,
  useDeleteMessage,
  useCreateOrgConversation,
} from "@/hooks/use-conversations";
import { useAuthStore } from "@/stores/auth.store";
import { ConversationList } from "@/components/chat/conversation-list";
import { MessageThread } from "@/components/chat/message-thread";
import { MessageInput } from "@/components/chat/message-input";
import { EmptyState } from "@/components/shared/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { MessageSquare } from "lucide-react";
import type { Conversation } from "@/types/conversation.types";

export default function MessagesPage() {
  const user = useAuthStore((s) => s.user);
  const { data: orgs = [], isLoading: orgsLoading } = useOrganizations();

  const [selectedOrgId, setSelectedOrgId] = useState<string | null>(null);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);

  // Auto-select first org
  const orgId = selectedOrgId ?? orgs[0]?.id ?? "";

  const { data: conversations = [], isLoading: convsLoading } =
    useOrgConversations(orgId);
  const activeId = activeConversationId ?? conversations[0]?.id ?? null;

  const { data: messages = [], isLoading: msgsLoading } = useMessages(
    activeId ?? ""
  );
  const sendMessage = useSendMessage(activeId ?? "");
  const deleteMessage = useDeleteMessage(activeId ?? "");
  const createConversation = useCreateOrgConversation(orgId);

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
  };

  const handleSelectOrg = (id: string) => {
    setSelectedOrgId(id);
    setActiveConversationId(null);
  };

  const handleCreate = () => {
    createConversation.mutate(undefined, {
      onSuccess: (conv: Conversation) => setActiveConversationId(conv.id),
    });
  };

  const handleSend = (content: string) => {
    if (!activeId) return;
    sendMessage.mutate({ content });
  };

  const handleDelete = (messageId: string) => {
    deleteMessage.mutate(messageId);
  };

  if (orgsLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-[600px] w-full" />
      </div>
    );
  }

  if (orgs.length === 0) {
    return (
      <div className="py-12">
        <EmptyState
          icon={MessageSquare}
          title="Sin organizaciones"
          description="Necesitas pertenecer a una organización para chatear."
        />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold tracking-tight">Mensajes</h1>

      {/* Org selector */}
      {orgs.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {orgs.map((org) => (
            <button
              key={org.id}
              onClick={() => handleSelectOrg(org.id)}
              className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                orgId === org.id
                  ? "border-primary bg-primary/10 text-primary"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {org.name}
            </button>
          ))}
        </div>
      )}

      {orgs.length === 1 && (
        <Badge variant="outline">{orgs[0].name}</Badge>
      )}

      {/* Chat panel */}
      <div className="flex h-[600px] overflow-hidden rounded-lg border">
        {/* Sidebar */}
        <div className="w-[280px] shrink-0 border-r">
          <ConversationList
            conversations={conversations}
            activeId={activeId}
            onSelect={handleSelectConversation}
            onCreateConversation={handleCreate}
            isLoading={convsLoading}
            isCreating={createConversation.isPending}
          />
        </div>

        {/* Messages */}
        <div className="flex flex-1 flex-col">
          {activeId && user ? (
            <>
              <MessageThread
                messages={messages}
                currentUserId={user.id}
                isLoading={msgsLoading}
                onDeleteMessage={handleDelete}
                isDeletingId={
                  deleteMessage.isPending
                    ? (deleteMessage.variables as string)
                    : null
                }
              />
              <MessageInput
                onSend={handleSend}
                isPending={sendMessage.isPending}
              />
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center p-8">
              <EmptyState
                icon={MessageSquare}
                title="Sin conversaciones"
                description="Crea una conversación para empezar a chatear."
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
