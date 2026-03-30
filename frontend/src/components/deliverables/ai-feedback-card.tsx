"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sparkles } from "lucide-react";

interface FeedbackItem {
  what: string;
  priority: "high" | "medium" | "low";
  suggestion: string;
}

interface AiFeedbackJson {
  items: FeedbackItem[];
  summary: string;
}

interface AiFeedbackCardProps {
  json: string;
  fallback: string;
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

export function AiFeedbackCard({ json, fallback }: AiFeedbackCardProps) {
  let parsedFeedback: AiFeedbackJson | null = null;

  try {
    parsedFeedback = JSON.parse(json);
  } catch {
    // JSON parsing failed — show fallback
  }

  if (!parsedFeedback || !Array.isArray(parsedFeedback.items)) {
    // Fallback: show original feedback text
    return (
      <Card className="p-4 mt-4 bg-muted/50 border-muted-foreground/20">
        <div className="flex items-start gap-2 mb-2">
          <Sparkles className="w-4 h-4 mt-0.5 text-muted-foreground" />
          <h3 className="text-sm font-semibold text-muted-foreground">
            Análisis AI
          </h3>
        </div>
        <p className="text-sm text-foreground/80">{fallback}</p>
      </Card>
    );
  }

  // Parsed successfully
  return (
    <Card className="p-4 mt-4 bg-muted/50 border-muted-foreground/20">
      <div className="flex items-start gap-2 mb-4">
        <Sparkles className="w-4 h-4 mt-0.5 text-accent" />
        <div>
          <h3 className="text-sm font-semibold">Análisis AI</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {parsedFeedback.summary}
          </p>
        </div>
      </div>

      <div className="space-y-3">
        {parsedFeedback.items.map((item, idx) => (
          <div
            key={idx}
            className="border-l-2 border-border pl-3 py-1"
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-sm font-medium text-foreground">{item.what}</p>
              <Badge
                variant={priorityColors[item.priority]}
                className="text-xs"
              >
                {priorityLabels[item.priority]}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">{item.suggestion}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
