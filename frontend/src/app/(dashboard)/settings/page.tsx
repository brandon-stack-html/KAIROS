"use client";

import { Settings } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Configuración</h1>
        <p className="text-muted-foreground">
          Ajustes de tu cuenta y preferencias
        </p>
      </div>

      <div className="flex flex-col items-center justify-center rounded-md border border-dashed p-12 text-center">
        <Settings className="mb-4 size-12 text-muted-foreground" />
        <h2 className="text-lg font-semibold">Próximamente</h2>
        <p className="text-sm text-muted-foreground">
          La configuración de cuenta estará disponible en el Sprint 4
        </p>
      </div>
    </div>
  );
}
