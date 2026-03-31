"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sparkles, X, ChevronDown, ChevronUp, CheckCircle2 } from "lucide-react";
import { useState } from "react";

interface ActionItem {
  task: string;
  assigned_to: string;
  deadline: string;
  priority: "high" | "medium" | "low";
  source_quote: string;
}

interface ActionItemsJson {
  action_items: ActionItem[];
  summary: string;
}

interface ActionItemsPanelProps {
  json: string;
  onClose: () => void;
}

const priorityColors = {
  high: "destructive",
  medium: "secondary",
  low: "outline",
} as const;

const priorityLabels = {
  high: "Alta",
  medium: "Media",
  low: "Baja",
} as const;

export function ActionItemsPanel({ json, onClose }: ActionItemsPanelProps) {
  const [expandedQuote, setExpandedQuote] = useState<number | null>(null);

  let parsedItems: ActionItemsJson | null = null;

  try {
    parsedItems = JSON.parse(json);
  } catch {
    // JSON parsing failed
  }

  if (!parsedItems || !Array.isArray(parsedItems.action_items)) {
    return (
      <Card className="p-4 bg-purple-500/5 border-purple-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-zinc-400">
              No se pudieron extraer tareas
            </span>
          </div>
          <Button size="sm" variant="ghost" onClick={onClose} className="h-6 w-6 p-0 text-zinc-500 hover:text-zinc-200">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    );
  }

  const { action_items, summary } = parsedItems;

  const priorityClasses = {
    high: "bg-red-500/10 text-red-400 border-red-500/20",
    medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    low: "bg-zinc-500/10 text-zinc-400 border-zinc-500/20",
  } as const;

  return (
    <Card className="p-4 bg-purple-500/5 border-purple-500/20">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-start gap-2 flex-1">
          <Sparkles className="w-4 h-4 mt-0.5 text-purple-400 flex-shrink-0" />
          <div>
            <h3 className="text-sm font-semibold text-white">Tareas extraídas</h3>
            <p className="text-xs text-zinc-400 mt-0.5">{summary}</p>
          </div>
        </div>
        <Button size="sm" variant="ghost" onClick={onClose} className="h-6 w-6 p-0 text-zinc-500 hover:text-zinc-200 flex-shrink-0">
          <X className="w-4 h-4" />
        </Button>
      </div>

      {action_items.length === 0 ? (
        <p className="text-xs text-zinc-500">No se encontraron tareas en la conversación</p>
      ) : (
        <div className="space-y-3">
          {action_items.map((item, idx) => (
            <div key={idx} className="border-l-2 border-purple-500/30 pl-3 py-1.5 bg-white/[0.02] rounded-r">
              <div className="flex items-start gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 mt-0.5 text-purple-400 flex-shrink-0" />
                <p className="text-sm font-medium text-zinc-200 break-words flex-1 min-w-0">
                  {item.task}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-1.5 mb-2 ml-6">
                {item.assigned_to !== "unassigned" && (
                  <span className="text-[10px] border border-white/[0.06] bg-white/[0.02] text-zinc-400 px-2 py-0.5 rounded-full">
                    👤 {item.assigned_to}
                  </span>
                )}
                {item.deadline !== "not specified" && (
                  <span className="text-[10px] border border-white/[0.06] bg-white/[0.02] text-zinc-400 px-2 py-0.5 rounded-full font-mono">
                    {item.deadline}
                  </span>
                )}
                <span className={`text-[10px] border px-2 py-0.5 rounded-full ${priorityClasses[item.priority]}`}>
                  {priorityLabels[item.priority]}
                </span>
              </div>

              <button
                onClick={() => setExpandedQuote(expandedQuote === idx ? null : idx)}
                className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 ml-6 transition-colors"
              >
                {expandedQuote === idx ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                <span>Fuente</span>
              </button>

              {expandedQuote === idx && (
                <p className="text-xs text-zinc-500 italic ml-6 mt-1.5 p-2 bg-white/[0.02] rounded border-l border-purple-500/20">
                  "{item.source_quote}"
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
