"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardStats } from "@/types/dashboard.types";

interface DeliverableChartProps {
  stats: DashboardStats;
}

const COLORS = {
  Pendiente: "#f59e0b",
  Aprobado: "#4ade80",
  Cambios: "#ef4444",
};

export function DeliverableChart({ stats }: DeliverableChartProps) {
  const data = [
    { name: "Pendiente", value: stats.deliverables_pending },
    { name: "Aprobado", value: stats.deliverables_approved },
    { name: "Cambios", value: stats.deliverables_changes_requested },
  ];

  return (
    <Card className="border-white/[0.06]">
      <CardHeader>
        <CardTitle className="text-sm font-medium">
          Entregables por estado
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart layout="vertical" data={data}>
            <XAxis type="number" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "#a1a1aa", fontSize: 12 }}
              width={80}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#18181b",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "6px",
                color: "#fafafa",
              }}
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {data.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={COLORS[entry.name as keyof typeof COLORS]}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
