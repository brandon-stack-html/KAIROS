"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useOrganization, useAcceptInvitation } from "@/hooks/use-organizations";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Building2, CheckCircle } from "lucide-react";
import { getApiErrorMessage } from "@/lib/api/axios-instance";

function AcceptInvitationContent() {
  const searchParams = useSearchParams();
  const orgId = searchParams.get("org_id");
  const invitationId = searchParams.get("invitation_id");

  const { data: org, isLoading: orgLoading } = useOrganization(orgId ?? "");
  const acceptInvitation = useAcceptInvitation();

  if (!orgId || !invitationId) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardContent className="flex flex-col items-center py-8 text-center gap-4">
            <p className="text-muted-foreground">Link de invitación inválido.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <Building2 className="size-10 text-primary mx-auto mb-2" />
          <CardTitle>Invitación a organización</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-6 text-center">
          {orgLoading ? (
            <Skeleton className="h-6 w-40" />
          ) : (
            <p className="text-muted-foreground">
              Has sido invitado a unirte a{" "}
              <span className="font-semibold text-foreground">
                {org?.name ?? "esta organización"}
              </span>
              .
            </p>
          )}

          {acceptInvitation.error && (
            <p className="text-sm text-destructive">
              {getApiErrorMessage(acceptInvitation.error)}
            </p>
          )}

          <Button
            className="w-full"
            onClick={() => acceptInvitation.mutate({ orgId, invitationId })}
            disabled={acceptInvitation.isPending}
          >
            <CheckCircle className="mr-2 size-4" />
            {acceptInvitation.isPending ? "Aceptando..." : "Aceptar invitación"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default function AcceptInvitationPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[400px]">
          <Skeleton className="h-64 w-full max-w-md" />
        </div>
      }
    >
      <AcceptInvitationContent />
    </Suspense>
  );
}
