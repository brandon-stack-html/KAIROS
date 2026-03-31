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
      <DialogContent className="sm:max-w-md border-white/[0.06] bg-zinc-950">
        <DialogHeader>
          <DialogTitle className="text-white">Subir documento</DialogTitle>
        </DialogHeader>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 transition-all duration-200 ${
            dragging
              ? "border-green-500/50 bg-green-500/5"
              : selected
              ? "border-green-500/30 bg-green-500/5"
              : "border-white/[0.1] hover:border-white/[0.2] hover:bg-white/[0.02]"
          }`}
        >
          <Upload className={`size-8 transition-colors ${dragging || selected ? "text-green-400" : "text-zinc-600"}`} />
          {selected ? (
            <div className="text-center">
              <p className="text-sm font-medium text-green-400">{selected.name}</p>
              <p className="text-xs text-zinc-500 mt-1">{(selected.size / 1024).toFixed(0)} KB</p>
            </div>
          ) : (
            <>
              <p className="text-sm font-medium text-zinc-200">
                Arrastra un archivo o haz clic
              </p>
              <p className="text-xs text-zinc-500">
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
          <Button variant="outline" className="border-white/[0.06] hover:bg-white/[0.04]" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button
            className="bg-green-500 text-black hover:bg-green-400"
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
