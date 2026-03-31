"use client";

import { Document } from "@/types/document.types";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  FileText,
  FileImage,
  FileArchive,
  File,
  Download,
  Trash2,
} from "lucide-react";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileIcon({ fileType }: { fileType: string }) {
  if (fileType === "application/pdf" || fileType.startsWith("text/"))
    return <FileText className="size-8 text-red-400" />;
  if (fileType.startsWith("image/"))
    return <FileImage className="size-8 text-cyan-400" />;
  if (fileType === "application/zip")
    return <FileArchive className="size-8 text-amber-400" />;
  return <File className="size-8 text-zinc-500" />;
}

interface DocumentCardProps {
  document: Document;
  onDelete?: (id: string) => void;
  downloadUrl: string;
  canDelete?: boolean;
}

export function DocumentCard({
  document,
  onDelete,
  downloadUrl,
  canDelete = false,
}: DocumentCardProps) {
  return (
    <Card className="group relative border-white/[0.06] transition-all duration-200 hover:border-white/[0.1] hover:bg-white/[0.02]">
      <CardContent className="flex items-start gap-3 p-4">
        <FileIcon fileType={document.file_type} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-white" title={document.filename}>
            {document.filename}
          </p>
          <p className="text-xs text-zinc-500 font-mono">
            {formatBytes(document.file_size_bytes)}
          </p>
          <p className="text-xs text-zinc-600 font-mono">
            {new Date(document.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-1">
          <Button
            size="icon"
            variant="ghost"
            className="size-8 text-zinc-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors"
            nativeButton={false}
            render={<a href={downloadUrl} download={document.filename} />}
          >
            <Download className="size-4" />
          </Button>
          {canDelete && onDelete && (
            <Button
              size="icon"
              variant="ghost"
              className="size-8 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
              onClick={() => onDelete(document.id)}
            >
              <Trash2 className="size-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
