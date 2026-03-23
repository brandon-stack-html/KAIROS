"use client";

import { useProjectSummary } from "@/hooks/use-projects";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Sparkles, RefreshCw, AlertCircle } from "lucide-react";
import { getApiErrorMessage } from "@/lib/api/axios-instance";

interface ProjectSummaryProps {
  projectId: string;
}

export function ProjectSummary({ projectId }: ProjectSummaryProps) {
  const {
    data,
    isFetching,
    isError,
    error,
    refetch,
  } = useProjectSummary(projectId);

  const hasData = !!data?.summary;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="size-5" />
          Resumen AI
        </CardTitle>
        <Button
          size="sm"
          variant={hasData ? "outline" : "default"}
          onClick={() => refetch()}
          disabled={isFetching}
        >
          {isFetching ? (
            <>
              <RefreshCw className="mr-2 size-4 animate-spin" />
              Generando...
            </>
          ) : hasData ? (
            <>
              <RefreshCw className="mr-2 size-4" />
              Regenerar
            </>
          ) : (
            <>
              <Sparkles className="mr-2 size-4" />
              Generar resumen
            </>
          )}
        </Button>
      </CardHeader>
      <CardContent>
        {isFetching && !hasData ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
        ) : isError ? (
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="size-4" />
            <span>{getApiErrorMessage(error)}</span>
          </div>
        ) : hasData ? (
          <div className="prose prose-sm max-w-none text-muted-foreground">
            <p className="whitespace-pre-wrap">{data.summary}</p>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            Haz clic en &quot;Generar resumen&quot; para obtener un análisis AI del
            estado del proyecto basado en sus entregables.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
