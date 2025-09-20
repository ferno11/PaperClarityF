"use client";

import * as React from "react";
import { Pie, PieChart, Cell, BarChart, Bar, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ShieldAlert, ShieldQuestion, ShieldCheck, AlertTriangle, TrendingUp } from "lucide-react";

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
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { Clause } from "@/lib/types";

type RiskOverviewProps = {
  clauses: Clause[];
};

const COLORS = {
  High: "#ef4444",
  Medium: "#f59e0b", 
  Low: "#10b981",
};

const riskConfig = {
  High: {
    label: "High Risk",
    icon: ShieldAlert,
    color: COLORS.High,
    bgColor: "bg-red-50 dark:bg-red-900/20",
    textColor: "text-red-700 dark:text-red-400",
  },
  Medium: {
    label: "Medium Risk", 
    icon: ShieldQuestion,
    color: COLORS.Medium,
    bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
    textColor: "text-yellow-700 dark:text-yellow-400",
  },
  Low: {
    label: "Low Risk",
    icon: ShieldCheck,
    color: COLORS.Low,
    bgColor: "bg-green-50 dark:bg-green-900/20",
    textColor: "text-green-700 dark:text-green-400",
  },
};

export function RiskOverview({ clauses }: RiskOverviewProps) {
  const { chartData, counts, totalClauses, riskScore } = React.useMemo(() => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    const totalClauses = clauses.length;
    
    clauses.forEach((clause) => {
      if (clause.risk_level in counts) {
        counts[clause.risk_level]++;
      }
    });
    
    const chartData = [
      { name: "High Risk", value: counts.High, fill: COLORS.High, count: counts.High },
      { name: "Medium Risk", value: counts.Medium, fill: COLORS.Medium, count: counts.Medium },
      { name: "Low Risk", value: counts.Low, fill: COLORS.Low, count: counts.Low },
    ].filter(item => item.value > 0);

    // Calculate risk score (0-100, higher is more risky)
    const riskScore = totalClauses > 0 
      ? Math.round(((counts.High * 3 + counts.Medium * 2 + counts.Low * 1) / (totalClauses * 3)) * 100)
      : 0;

    return { chartData, counts, totalClauses, riskScore };
  }, [clauses]);

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { level: "High", color: "text-red-600", bg: "bg-red-100" };
    if (score >= 40) return { level: "Medium", color: "text-yellow-600", bg: "bg-yellow-100" };
    return { level: "Low", color: "text-green-600", bg: "bg-green-100" };
  };

  const riskLevel = getRiskLevel(riskScore);

  if (totalClauses === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Risk Overview
          </CardTitle>
          <CardDescription>
            No clauses found to analyze.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            Upload a document to see risk analysis.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Risk Score Card */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5" />
            Overall Risk Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{riskScore}/100</span>
              <Badge className={`${riskLevel.bg} ${riskLevel.color} border-0`}>
                {riskLevel.level} Risk
              </Badge>
            </div>
            <Progress value={riskScore} className="h-2" />
            <p className="text-xs text-muted-foreground">
              Based on {totalClauses} clause{totalClauses !== 1 ? 's' : ''} analyzed
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Risk Distribution */}
      <Card>
        <CardHeader>
          <CardTitle>Risk Distribution</CardTitle>
          <CardDescription>
            Breakdown of clauses by risk level.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {chartData.length > 0 ? (
            <div className="space-y-4">
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
                    innerRadius={40}
                    outerRadius={80}
                    strokeWidth={2}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                </PieChart>
              </ChartContainer>
              
              {/* Risk Statistics */}
              <div className="space-y-2">
                {Object.entries(counts).map(([level, count]) => {
                  const config = riskConfig[level as keyof typeof riskConfig];
                  if (!config || count === 0) return null;
                  
                  const percentage = Math.round((count / totalClauses) * 100);
                  const Icon = config.icon;
                  
                  return (
                    <div key={level} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <Icon className={`h-4 w-4 ${config.textColor}`} />
                        <span className="font-medium">{config.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{count}</span>
                        <span className="text-xs text-muted-foreground">({percentage}%)</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center text-muted-foreground">
              No risk data to display.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
