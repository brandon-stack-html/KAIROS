"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SendHorizontal } from "lucide-react";
import { useState, useCallback, type KeyboardEvent } from "react";

interface MessageInputProps {
  onSend: (content: string) => void;
  isPending?: boolean;
}

export function MessageInput({ onSend, isPending }: MessageInputProps) {
  const [content, setContent] = useState("");

  const handleSend = useCallback(() => {
    const trimmed = content.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setContent("");
  }, [content, onSend]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end gap-2 border-t border-white/[0.06] p-3 bg-white/[0.01]">
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Escribe un mensaje... (Enter para enviar)"
        className="min-h-[40px] max-h-[120px] resize-none bg-zinc-900/50 border-zinc-800 text-white placeholder:text-zinc-600 rounded-xl"
        rows={1}
        disabled={isPending}
      />
      <Button
        size="icon"
        onClick={handleSend}
        disabled={isPending || !content.trim()}
        className="bg-green-500 text-black hover:bg-green-400 rounded-xl transition-colors duration-150 shrink-0"
      >
        <SendHorizontal className="size-4" />
      </Button>
    </div>
  );
}
