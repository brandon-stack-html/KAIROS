"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Upload } from "lucide-react";

interface DocumentUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onUpload: (file: File) => void;
  isPending?: boolean;
}

export function DocumentUploadDialog({
  open,
  onOpenChange,
  onUpload,
  isPending = false,
}: DocumentUploadDialogProps) {
  const [dragging, setDragging] = useState(false);
  const [selected, setSelected] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(file: File) {
    setSelected(file);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function handleSubmit() {
    if (!selected) return;
    onUpload(selected);
    setSelected(null);
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Subir documento</DialogTitle>
        </DialogHeader>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 transition-colors ${
            dragging
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/30 hover:border-primary/50"
          }`}
        >
          <Upload className="size-8 text-muted-foreground" />
          {selected ? (
            <p className="text-sm font-medium">{selected.name}</p>
          ) : (
            <>
              <p className="text-sm font-medium">
                Arrastra un archivo o haz clic
              </p>
              <p className="text-xs text-muted-foreground">
                PDF, imágenes, Word, ZIP, TXT — máx. 10 MB
              </p>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            onChange={handleChange}
            accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.doc,.docx,.zip,.txt"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!selected || isPending}
          >
            {isPending ? "Subiendo…" : "Subir"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
