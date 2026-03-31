"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import type { Conversation } from "@/types/conversation.types";
import { ConversationType } from "@/types/conversation.types";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { MessageSquarePlus } from "lucide-react";

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onCreateConversation?: () => void;
  isLoading?: boolean;
  isCreating?: boolean;
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
  onCreateConversation,
  isLoading,
  isCreating,
}: ConversationListProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2 p-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-16 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {onCreateConversation && (
        <div className="border-b border-white/[0.06] p-3">
          <Button
            size="sm"
            className="w-full bg-green-500 text-black hover:bg-green-400 transition-colors duration-150"
            onClick={onCreateConversation}
            disabled={isCreating}
          >
            <MessageSquarePlus className="mr-2 size-4" />
            {isCreating ? "Creando..." : "Nueva conversación"}
          </Button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <p className="p-4 text-center text-sm text-zinc-500">
            No hay conversaciones
          </p>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={`flex w-full items-center gap-3 border-b border-white/[0.04] px-4 py-3 text-left transition-colors hover:bg-white/[0.02] ${
                activeId === conv.id
                  ? "bg-white/[0.04] border-l-2 border-l-green-500"
                  : ""
              }`}
            >
              <div className="flex flex-col gap-1 min-w-0">
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-500 shrink-0" />
                  <Badge className="text-[10px] border-white/[0.06] bg-white/[0.02] text-zinc-400 shrink-0">
                    {conv.type === ConversationType.ORG ? "Org" : "Proyecto"}
                  </Badge>
                  <span className="text-xs text-zinc-500 truncate font-mono">
                    {conv.id.slice(0, 8)}
                  </span>
                </div>
                <span className="text-xs text-zinc-600">
                  {formatDistanceToNow(new Date(conv.created_at), {
                    addSuffix: true,
                    locale: es,
                  })}
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
