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
    return <FileImage className="size-8 text-blue-400" />;
  if (fileType === "application/zip")
    return <FileArchive className="size-8 text-yellow-400" />;
  return <File className="size-8 text-muted-foreground" />;
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
    <Card className="group relative">
      <CardContent className="flex items-start gap-3 p-4">
        <FileIcon fileType={document.file_type} />
        <div className="min-w-0 flex-1">
          <p
            className="truncate text-sm font-medium"
            title={document.filename}
          >
            {document.filename}
          </p>
          <p className="text-xs text-muted-foreground">
            {formatBytes(document.file_size_bytes)}
          </p>
          <p className="text-xs text-muted-foreground">
            {new Date(document.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-1">
          <Button
            size="icon"
            variant="ghost"
            className="size-8"
            nativeButton={false}
            render={<a href={downloadUrl} download={document.filename} />}
          >
            <Download className="size-4" />
          </Button>
          {canDelete && onDelete && (
            <Button
              size="icon"
              variant="ghost"
              className="size-8 text-destructive hover:text-destructive"
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
