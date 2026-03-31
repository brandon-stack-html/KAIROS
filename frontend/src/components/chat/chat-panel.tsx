"use client";

import { useState } from "react";
import { ConversationList } from "./conversation-list";
import { MessageThread } from "./message-thread";
import { MessageInput } from "./message-input";
import { ActionItemsPanel } from "./action-items-panel";
import { Button } from "@/components/ui/button";
import {
  useOrgConversations,
  useMessages,
  useSendMessage,
  useDeleteMessage,
  useCreateOrgConversation,
  useCreateProjectConversation,
  useExtractActions,
} from "@/hooks/use-conversations";
import { useAuthStore } from "@/stores/auth.store";
import { ConversationType } from "@/types/conversation.types";
import { MessageSquare, Sparkles } from "lucide-react";
import { EmptyState } from "@/components/shared/empty-state";

interface ChatPanelProps {
  orgId: string;
  projectId?: string;
}

export function ChatPanel({ orgId, projectId }: ChatPanelProps) {
  const user = useAuthStore((s) => s.user);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [showActionItems, setShowActionItems] = useState(false);
  const [actionItemsJson, setActionItemsJson] = useState<string | null>(null);

  const { data: allConversations = [], isLoading: isLoadingConvs } =
    useOrgConversations(orgId);

  // Filter conversations by context
  const conversations = projectId
    ? allConversations.filter(
        (c) =>
          c.type === ConversationType.PROJECT && c.project_id === projectId
      )
    : allConversations;

  const activeId = activeConversationId ?? conversations[0]?.id ?? null;

  const { data: messages = [], isLoading: isLoadingMsgs } = useMessages(
    activeId ?? ""
  );
  const sendMessage = useSendMessage(activeId ?? "");
  const deleteMessage = useDeleteMessage(activeId ?? "");
  const extractActions = useExtractActions(activeId ?? "");

  const createOrgConversation = useCreateOrgConversation(orgId);
  const createProjectConversation = useCreateProjectConversation();

  const handleCreateConversation = () => {
    if (projectId) {
      createProjectConversation.mutate(projectId, {
        onSuccess: (conv) => setActiveConversationId(conv.id),
      });
    } else {
      createOrgConversation.mutate(undefined, {
        onSuccess: (conv) => setActiveConversationId(conv.id),
      });
    }
  };

  const handleSend = (content: string) => {
    if (!activeId) return;
    sendMessage.mutate({ content });
  };

  const handleDelete = (messageId: string) => {
    deleteMessage.mutate(messageId);
  };

  const handleExtractActions = () => {
    if (!activeId) return;
    extractActions.mutate(undefined, {
      onSuccess: (data) => {
        setActionItemsJson(data.ai_action_items);
        setShowActionItems(true);
      },
    });
  };

  if (!user) return null;

  return (
    <div className="flex h-full min-h-[500px] overflow-hidden rounded-xl border border-white/[0.06] bg-[#09090b]">
      {/* Sidebar — conversation list */}
      <div className="w-[260px] shrink-0 border-r border-white/[0.06]">
        <ConversationList
          conversations={conversations}
          activeId={activeId}
          onSelect={setActiveConversationId}
          onCreateConversation={handleCreateConversation}
          isLoading={isLoadingConvs}
          isCreating={
            createOrgConversation.isPending ||
            createProjectConversation.isPending
          }
        />
      </div>

      {/* Main — messages */}
      <div className="flex flex-1 flex-col min-w-0">
        {activeId ? (
          <>
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06] bg-white/[0.01]">
              <div className="text-sm text-zinc-400">
                {conversations.find((c) => c.id === activeId)?.type === ConversationType.PROJECT
                  ? "Chat del proyecto"
                  : "Chat de la organización"}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleExtractActions}
                disabled={extractActions.isPending || messages.length === 0}
                className="gap-2 border-purple-500/20 hover:border-purple-500/40 hover:bg-purple-500/10 text-purple-400 text-xs"
              >
                <Sparkles className="w-3.5 h-3.5" />
                {extractActions.isPending ? "Analizando..." : "Extraer tareas"}
              </Button>
            </div>

            {/* Action items panel */}
            {showActionItems && actionItemsJson && (
              <div className="px-4 py-3 border-b border-white/[0.06]">
                <ActionItemsPanel
                  json={actionItemsJson}
                  onClose={() => {
                    setShowActionItems(false);
                    setActionItemsJson(null);
                  }}
                />
              </div>
            )}

            {/* Messages */}
            <MessageThread
              messages={messages}
              currentUserId={user.id}
              isLoading={isLoadingMsgs}
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
              description="Crea una conversación para empezar a chatear con tu equipo."
            />
          </div>
        )}
      </div>
    </div>
  );
}
