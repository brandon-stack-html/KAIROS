"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { OrganizationForm } from "@/components/organizations/organization-form";

export default function NewOrganizationPage() {
  return (
    <div className="max-w-lg">
      <Card>
        <CardHeader>
          <CardTitle>Nueva organización</CardTitle>
          <CardDescription>
            Crea una organización para gestionar proyectos, miembros y facturas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <OrganizationForm />
        </CardContent>
      </Card>
    </div>
  );
}
