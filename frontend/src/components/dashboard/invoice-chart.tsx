"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { DashboardStats } from "@/types/dashboard.types";

interface InvoiceChartProps {
  stats: DashboardStats;
}

const COLORS = ["#4ade80", "#f59e0b"];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("es-MX", { style: "currency", currency: "USD" }).format(
    value
  );

export function InvoiceChart({ stats }: InvoiceChartProps) {
  const paid = parseFloat(stats.invoices_paid_amount);
  const pending = parseFloat(stats.invoices_pending_amount);
  const total = parseFloat(stats.invoices_total_amount);

  const data = [
    { name: "Pagado", value: paid },
    { name: "Pendiente", value: pending },
  ];

  const isEmpty = paid === 0 && pending === 0;

  return (
    <Card className="border-white/[0.06]">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Estado de facturas</CardTitle>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <div className="flex items-center justify-center h-[180px] text-sm text-zinc-500">
            No hay facturas registradas aún.
          </div>
        ) : (
          <div className="relative">
            <ResponsiveContainer width="100%" height={180}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {data.map((entry, index) => (
                    <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "1px solid rgba(255,255,255,0.06)",
                    borderRadius: "6px",
                    color: "#fafafa",
                  }}
                  formatter={(value) => formatCurrency(Number(value))}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <p className="text-xs text-zinc-500">Total</p>
              <p className="text-sm font-semibold text-white font-mono">{formatCurrency(total)}</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
