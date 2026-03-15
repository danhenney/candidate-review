"use client";

import { Evaluation } from "@/lib/api";

const recStyle: Record<string, string> = {
  통과: "bg-green-100 text-green-800 border-green-300",
  검토: "bg-yellow-100 text-yellow-800 border-yellow-300",
  탈락: "bg-red-100 text-red-800 border-red-300",
};

export default function EvaluationReport({
  evaluation,
}: {
  evaluation: Evaluation;
}) {
  const style = recStyle[evaluation.recommendation] || recStyle["검토"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <div
          className={`px-4 py-2 rounded-lg border font-bold text-lg ${style}`}
        >
          {evaluation.recommendation}
        </div>
        <div className="text-3xl font-bold text-gray-900">
          {evaluation.overall_score}점
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white p-5 rounded-lg shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-2">종합 평가</h3>
        <p className="text-gray-700 leading-relaxed">{evaluation.summary}</p>
      </div>

      {/* Per-dimension scores */}
      <div className="bg-white p-5 rounded-lg shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-4">항목별 평가</h3>
        <div className="space-y-4">
          {Object.entries(evaluation.scores).map(([name, val]) => (
            <div key={name}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700">
                  {name}
                </span>
                <span className="text-sm font-bold text-gray-900">
                  {val.score}/{val.max}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{
                    width: `${(val.score / val.max) * 100}%`,
                  }}
                />
              </div>
              <p className="text-sm text-gray-600">{val.reasoning}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Risks */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-5 rounded-lg shadow-sm">
          <h3 className="font-semibold text-green-700 mb-3">강점</h3>
          <ul className="space-y-2">
            {evaluation.strengths.map((s, i) => (
              <li key={i} className="text-sm text-gray-700 flex gap-2">
                <span className="text-green-500 flex-shrink-0">+</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm">
          <h3 className="font-semibold text-red-700 mb-3">리스크</h3>
          <ul className="space-y-2">
            {evaluation.risks.map((r, i) => (
              <li key={i} className="text-sm text-gray-700 flex gap-2">
                <span className="text-red-500 flex-shrink-0">!</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Meta */}
      <p className="text-xs text-gray-400">
        모델: {evaluation.model_used} | 토큰: {evaluation.tokens_used.toLocaleString()} |{" "}
        {new Date(evaluation.created_at).toLocaleString("ko-KR")}
      </p>
    </div>
  );
}
