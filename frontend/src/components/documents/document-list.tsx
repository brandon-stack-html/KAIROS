"use client";

import { useState } from "react";
import { Document } from "@/types/document.types";
import { DocumentCard } from "./document-card";
import { DocumentUploadDialog } from "./document-upload-dialog";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { documentsApi } from "@/lib/api/documents.api";

interface DocumentListProps {
  documents: Document[];
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
  isPendingUpload?: boolean;
  currentUserId?: string;
}

export function DocumentList({
  documents,
  onUpload,
  onDelete,
  isPendingUpload = false,
  currentUserId,
}: DocumentListProps) {
  const [uploadOpen, setUploadOpen] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-zinc-500">
          {documents.length}{" "}
          {documents.length === 1 ? "documento" : "documentos"}
        </p>
        <Button size="sm" className="bg-green-500 text-black hover:bg-green-400" onClick={() => setUploadOpen(true)}>
          <Upload className="mr-2 size-4" />
          Subir archivo
        </Button>
      </div>

      {documents.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.02] py-12 text-center">
          <Upload className="mb-3 size-10 text-zinc-600" />
          <p className="text-sm text-zinc-500">
            No hay documentos. Sube el primero.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onDelete={onDelete}
              downloadUrl={documentsApi.downloadUrl(doc.id)}
              canDelete={
                currentUserId === doc.uploaded_by || !!currentUserId
              }
            />
          ))}
        </div>
      )}

      <DocumentUploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        onUpload={onUpload}
        isPending={isPendingUpload}
      />
    </div>
  );
}
