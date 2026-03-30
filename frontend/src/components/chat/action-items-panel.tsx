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
    // Fallback: show error message
    return (
      <Card className="p-4 bg-muted/50 border-muted-foreground/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">
              No se pudieron extraer tareas
            </span>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="h-6 w-6 p-0"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </Card>
    );
  }

  const { action_items, summary } = parsedItems;

  return (
    <Card className="p-4 bg-muted/50 border-muted-foreground/20">
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex items-start gap-2 flex-1">
          <Sparkles className="w-4 h-4 mt-0.5 text-accent flex-shrink-0" />
          <div>
            <h3 className="text-sm font-semibold">Tareas extraídas</h3>
            <p className="text-xs text-muted-foreground mt-0.5">{summary}</p>
          </div>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={onClose}
          className="h-6 w-6 p-0 flex-shrink-0"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>

      {action_items.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          No se encontraron tareas en la conversación
        </p>
      ) : (
        <div className="space-y-3">
          {action_items.map((item, idx) => (
            <div
              key={idx}
              className="border-l-2 border-border pl-3 py-2 bg-background/50 rounded-r px-3"
            >
              {/* Task header */}
              <div className="flex items-start gap-2 mb-2">
                <CheckCircle2 className="w-4 h-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground break-words">
                    {item.task}
                  </p>
                </div>
              </div>

              {/* Task metadata */}
              <div className="flex flex-wrap items-center gap-2 mb-2 ml-6">
                {item.assigned_to !== "unassigned" && (
                  <Badge variant="outline" className="text-xs">
                    👤 {item.assigned_to}
                  </Badge>
                )}
                {item.deadline !== "not specified" && (
                  <Badge variant="secondary" className="text-xs">
                    📅 {item.deadline}
                  </Badge>
                )}
                <Badge
                  variant={priorityColors[item.priority]}
                  className="text-xs"
                >
                  {priorityLabels[item.priority]}
                </Badge>
              </div>

              {/* Source quote (collapsible) */}
              <button
                onClick={() =>
                  setExpandedQuote(expandedQuote === idx ? null : idx)
                }
                className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground ml-6 transition-colors"
              >
                {expandedQuote === idx ? (
                  <ChevronUp className="w-3 h-3" />
                ) : (
                  <ChevronDown className="w-3 h-3" />
                )}
                <span>Fuente</span>
              </button>

              {expandedQuote === idx && (
                <p className="text-xs text-muted-foreground italic ml-6 mt-1 p-2 bg-muted rounded border-l border-muted-foreground">
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
