"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface ScoreData {
  [key: string]: { score: number; max: number; reasoning: string };
}

export default function ScoreRadar({ scores }: { scores: ScoreData }) {
  const data = Object.entries(scores).map(([name, val]) => ({
    dimension: name,
    score: val.score,
    max: val.max,
    fullMark: val.max,
  }));

  if (data.length === 0) return null;

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fontSize: 12, fill: "#374151" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 10]}
            tick={{ fontSize: 10, fill: "#9ca3af" }}
          />
          <Radar
            name="점수"
            dataKey="score"
            stroke="#2563eb"
            fill="#3b82f6"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip
            formatter={(value: number) => [`${value}점`, "점수"]}
            labelStyle={{ fontWeight: "bold" }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
