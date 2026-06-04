"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { ExposureItem } from "@/lib/types";

// Neutral multi-color palette — no red/green (avoids implying quality)
const COLORS = [
  "#2563EB", "#0D9488", "#7C3AED", "#D97706", "#0891B2",
  "#BE185D", "#16A34A", "#6366F1", "#B45309", "#475569",
];

interface Props {
  data: ExposureItem[];
  title?: string;
  sourceUrl?: string | null;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function ExposureChart({ data, title: _title, sourceUrl }: Props) {
  const chartData = data.map((d) => ({
    name: d.label,
    value: typeof d.weight === "number" ? d.weight : parseFloat(d.weight) || 0,
  }));

  return (
    <div className="flex flex-col gap-2">
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => [`${value.toFixed(2)}%`, "Weight"]}
            contentStyle={{ fontSize: 12 }}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ fontSize: 11, color: "#64748B" }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="text-[11px] text-missing-gray space-y-0.5">
        {sourceUrl && <p>Source: {new URL(sourceUrl).hostname}</p>}
        <p>Note: Charts display only corpus-available factual data.</p>
      </div>
    </div>
  );
}
