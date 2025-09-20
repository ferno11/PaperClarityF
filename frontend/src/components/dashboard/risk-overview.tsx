"use client";

import * as React from "react";
import { Pie, PieChart, Cell } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import type { Clause } from "@/lib/types";

type RiskOverviewProps = {
  clauses: Clause[];
};

const COLORS = {
  High: "hsl(var(--chart-4))",
  Medium: "hsl(var(--chart-2))",
  Low: "hsl(var(--chart-3))",
};

export function RiskOverview({ clauses }: RiskOverviewProps) {
  const chartData = React.useMemo(() => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    clauses.forEach((clause) => {
      if (clause.riskLevel in counts) {
        counts[clause.riskLevel]++;
      }
    });
    return [
      { name: "High Risk", value: counts.High, fill: COLORS.High },
      { name: "Medium Risk", value: counts.Medium, fill: COLORS.Medium },
      { name: "Low Risk", value: counts.Low, fill: COLORS.Low },
    ].filter(item => item.value > 0);
  }, [clauses]);

  const totalClauses = clauses.length;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risk Overview</CardTitle>
        <CardDescription>
          Distribution of risk levels across the document.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center">
        {totalClauses > 0 && chartData.length > 0 ? (
          <ChartContainer config={{}} className="mx-auto aspect-square h-48">
            <PieChart>
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent hideLabel />}
              />
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                innerRadius={60}
                strokeWidth={5}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
            </PieChart>
          </ChartContainer>
        ) : (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            No risk data to display.
          </div>
        )}
      </CardContent>
    </Card>
  );
}
