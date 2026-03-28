"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import type { Message } from "@/types/conversation.types";
import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { Trash2 } from "lucide-react";
import { useEffect, useRef } from "react";

interface MessageThreadProps {
  messages: Message[];
  currentUserId: string;
  isLoading?: boolean;
  onDeleteMessage?: (messageId: string) => void;
  isDeletingId?: string | null;
}

function getInitials(id: string) {
  return id.slice(0, 2).toUpperCase();
}

export function MessageThread({
  messages,
  currentUserId,
  isLoading,
  onDeleteMessage,
  isDeletingId,
}: MessageThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  if (isLoading) {
    return (
      <div className="flex flex-1 flex-col gap-4 p-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className={`flex gap-3 ${i % 2 === 0 ? "" : "flex-row-reverse"}`}>
            <Skeleton className="size-8 shrink-0 rounded-full" />
            <Skeleton className="h-16 w-2/3 rounded-lg" />
          </div>
        ))}
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-muted-foreground">
          No hay mensajes. Envía el primero.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
      {messages.map((msg) => {
        const isOwn = msg.sender_id === currentUserId;

        return (
          <div
            key={msg.id}
            className={`group flex gap-3 ${isOwn ? "flex-row-reverse" : ""}`}
          >
            <Avatar className="size-8 shrink-0">
              <AvatarFallback className="text-xs">
                {getInitials(msg.sender_id)}
              </AvatarFallback>
            </Avatar>

            <div
              className={`relative max-w-[70%] rounded-lg px-3 py-2 ${
                isOwn
                  ? "bg-green-950/30 text-foreground"
                  : "bg-card text-foreground"
              }`}
            >
              <div className="mb-1 flex items-center gap-2">
                <span className="font-mono text-xs text-muted-foreground">
                  {msg.sender_id.slice(0, 8)}
                </span>
                <span className="font-mono text-xs text-muted-foreground/60">
                  {formatDistanceToNow(new Date(msg.created_at), {
                    addSuffix: true,
                    locale: es,
                  })}
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>

              {isOwn && onDeleteMessage && (
                <button
                  onClick={() => onDeleteMessage(msg.id)}
                  disabled={isDeletingId === msg.id}
                  className="absolute -right-2 -top-2 hidden rounded-full bg-destructive p-1 text-destructive-foreground opacity-0 transition-opacity group-hover:block group-hover:opacity-100"
                  title="Eliminar mensaje"
                >
                  <Trash2 className="size-3" />
                </button>
              )}
            </div>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
