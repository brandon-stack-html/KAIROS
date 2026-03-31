"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users } from "lucide-react";
import { Organization } from "@/types/organization.types";

interface OrganizationCardProps {
  organization: Organization;
}

export function OrganizationCard({ organization }: OrganizationCardProps) {
  const initials = organization.name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <Link href={`/organizations/${organization.id}`}>
      <Card className="border-white/[0.06] transition-all duration-200 hover:border-white/[0.1] hover:bg-white/[0.02] cursor-pointer">
        <CardHeader className="pb-2">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-green-500/10 text-green-400 font-bold text-sm flex items-center justify-center shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg">{organization.name}</CardTitle>
              <p className="text-xs font-mono text-zinc-500 mt-0.5">
                /{organization.slug}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-1.5 text-xs text-zinc-500 uppercase tracking-widest">
            <Users className="size-4" />
            <span>
              {organization.members.length}{" "}
              {organization.members.length === 1 ? "miembro" : "miembros"}
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
