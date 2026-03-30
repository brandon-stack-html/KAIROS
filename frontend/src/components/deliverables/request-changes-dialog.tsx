"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useRequestChanges, useGenerateFeedback } from "@/hooks/use-deliverables";
import { AiFeedbackResponse } from "@/lib/api/deliverables.api";
import { AiFeedbackCard } from "./ai-feedback-card";
import { toast } from "sonner";

interface RequestChangesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  deliverableId: string | null;
  projectId: string;
}

export function RequestChangesDialog({
  open,
  onOpenChange,
  deliverableId,
  projectId,
}: RequestChangesDialogProps) {
  const [feedbackText, setFeedbackText] = useState("");
  const [aiFeedback, setAiFeedback] = useState<AiFeedbackResponse | null>(null);
  const [isGeneratingFeedback, setIsGeneratingFeedback] = useState(false);

  const requestChangesMutation = useRequestChanges(projectId);
  const generateFeedbackMutation = useGenerateFeedback();

  const isLoading = requestChangesMutation.isPending;
  const isFeedbackLoading = isGeneratingFeedback;

  async function handleSubmit() {
    if (!deliverableId) return;
    if (!feedbackText.trim()) {
      toast.error("Proporciona feedback para solicitar cambios");
      return;
    }

    try {
      // Step 1: Request changes (update deliverable status)
      await new Promise<void>((resolve, reject) => {
        requestChangesMutation.mutate(deliverableId, {
          onSuccess: () => resolve(),
          onError: reject,
        });
      });

      // Step 2: Generate AI feedback (fire-and-forget, non-blocking)
      setIsGeneratingFeedback(true);
      try {
        const feedback = await generateFeedbackMutation.mutateAsync({
          id: deliverableId,
          feedbackText,
        });
        setAiFeedback(feedback);
      } catch (error) {
        console.warn("AI feedback generation failed, but request-changes succeeded");
        toast.warning("Cambios solicitados, pero el análisis AI no pudo generarse");
      } finally {
        setIsGeneratingFeedback(false);
      }
    } catch (error) {
      // request-changes mutation already handled error via toast
      console.error(error);
    }
  }

  function handleClose() {
    setFeedbackText("");
    setAiFeedback(null);
    setIsGeneratingFeedback(false);
    onOpenChange(false);
  }

  // Validation
  const feedbackLength = feedbackText.trim().length;
  const isValidFeedback = feedbackLength >= 1 && feedbackLength <= 2000;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Solicitar cambios</DialogTitle>
          <DialogDescription>
            Describe los cambios necesarios. Nuestro AI generará un análisis estructurado.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Feedback del cliente</label>
            <Textarea
              placeholder="Ej: El logo está muy grande, los colores no van con la marca, falta el CTA..."
              className="mt-2 resize-none"
              rows={4}
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              disabled={isLoading || isFeedbackLoading}
            />
            <p className="text-xs text-muted-foreground mt-1">
              {feedbackLength} / 2000 caracteres
            </p>
          </div>

          {aiFeedback && (
            <AiFeedbackCard
              json={aiFeedback.ai_structured_feedback}
              fallback={aiFeedback.feedback_text}
            />
          )}

          {isFeedbackLoading && (
            <div className="p-3 bg-muted/50 rounded-md text-sm text-muted-foreground">
              Generando análisis AI...
            </div>
          )}
        </div>

        <DialogFooter className="pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isLoading || isFeedbackLoading}
          >
            Cancelar
          </Button>
          <Button
            type="submit"
            disabled={!isValidFeedback || isLoading || isFeedbackLoading}
            onClick={handleSubmit}
          >
            {isLoading ? "Enviando..." : "Solicitar cambios"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
