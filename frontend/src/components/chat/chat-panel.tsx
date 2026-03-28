"use client";

import { useState } from "react";
import { ConversationList } from "./conversation-list";
import { MessageThread } from "./message-thread";
import { MessageInput } from "./message-input";
import {
  useOrgConversations,
  useMessages,
  useSendMessage,
  useDeleteMessage,
  useCreateOrgConversation,
  useCreateProjectConversation,
} from "@/hooks/use-conversations";
import { useAuthStore } from "@/stores/auth.store";
import { ConversationType } from "@/types/conversation.types";
import { MessageSquare } from "lucide-react";
import { EmptyState } from "@/components/shared/empty-state";

interface ChatPanelProps {
  orgId: string;
  projectId?: string;
}

export function ChatPanel({ orgId, projectId }: ChatPanelProps) {
  const user = useAuthStore((s) => s.user);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

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

  if (!user) return null;

  return (
    <div className="flex h-[600px] overflow-hidden rounded-lg border">
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
