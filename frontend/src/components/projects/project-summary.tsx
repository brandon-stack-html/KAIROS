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
    <Card className="border-purple-500/20 bg-purple-500/[0.03]">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-lg flex items-center gap-2">
          <Sparkles className="size-5 text-purple-400" />
          <span>Resumen AI</span>
        </CardTitle>
        <Button
          size="sm"
          onClick={() => refetch()}
          disabled={isFetching}
          className={hasData
            ? "border-purple-500/20 hover:border-purple-500/40 hover:bg-purple-500/10 text-purple-400 border bg-transparent"
            : "bg-purple-500 text-white hover:bg-purple-600"
          }
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
          <div className="flex items-center gap-2 text-sm text-red-400">
            <AlertCircle className="size-4" />
            <span>{getApiErrorMessage(error)}</span>
          </div>
        ) : hasData ? (
          <p className="whitespace-pre-wrap text-sm text-zinc-300 leading-relaxed">
            {data.summary}
          </p>
        ) : (
          <p className="text-sm text-zinc-500 leading-relaxed">
            Haz clic en &quot;Generar resumen&quot; para obtener un análisis AI del
            estado del proyecto basado en sus entregables.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
