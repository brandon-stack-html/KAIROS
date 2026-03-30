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
    <div className="flex h-full min-h-[500px] overflow-hidden rounded-xl ring-1 ring-foreground/10">
      {/* Sidebar — conversation list */}
      <div className="w-[280px] shrink-0 border-r">
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
      <div className="flex flex-1 flex-col">
        {activeId ? (
          <>
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 border-b bg-background/50">
              <div className="text-sm text-muted-foreground">
                {conversations.find((c) => c.id === activeId)?.type === ConversationType.PROJECT
                  ? "Chat del proyecto"
                  : "Chat de la organización"}
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={handleExtractActions}
                disabled={extractActions.isPending || messages.length === 0}
                className="gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Extraer tareas
              </Button>
            </div>

            {/* Action items panel */}
            {showActionItems && actionItemsJson && (
              <div className="px-4 py-3 border-b">
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
