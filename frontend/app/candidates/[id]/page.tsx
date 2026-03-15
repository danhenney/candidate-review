"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Candidate } from "@/lib/api";
import ScoreRadar from "@/components/ScoreRadar";
import EvaluationReport from "@/components/EvaluationReport";

export default function ReviewPage() {
  const params = useParams();
  const id = Number(params.id);
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCandidate = () => {
    api.candidates
      .get(id)
      .then(setCandidate)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchCandidate();
    // Poll if evaluating
    const interval = setInterval(() => {
      api.candidates.get(id).then((c) => {
        setCandidate(c);
        if (c.status !== "evaluating") clearInterval(interval);
      });
    }, 5000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading) {
    return <p className="text-center py-12 text-gray-500">불러오는 중...</p>;
  }

  if (error || !candidate) {
    return (
      <p className="text-center py-12 text-red-500">
        {error || "후보를 찾을 수 없습니다"}
      </p>
    );
  }

  const latestEval =
    candidate.evaluations.length > 0
      ? candidate.evaluations[candidate.evaluations.length - 1]
      : null;

  const handleReEvaluate = async () => {
    try {
      await api.evaluations.trigger(candidate.id);
      fetchCandidate();
    } catch (e) {
      alert(e instanceof Error ? e.message : "오류 발생");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <a
            href="/"
            className="text-sm text-gray-500 hover:text-gray-700 mb-1 inline-block"
          >
            &larr; 목록으로
          </a>
          <h1 className="text-2xl font-bold text-gray-900">{candidate.name}</h1>
          {candidate.notes && (
            <p className="text-gray-500 mt-1">{candidate.notes}</p>
          )}
        </div>
        <button
          onClick={handleReEvaluate}
          disabled={candidate.status === "evaluating"}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {candidate.status === "evaluating" ? "평가 진행 중..." : "재평가"}
        </button>
      </div>

      {/* Status banner */}
      {candidate.status === "evaluating" && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-blue-700 text-sm">
          AI 평가가 진행 중입니다. 잠시만 기다려주세요...
        </div>
      )}

      {candidate.status === "error" && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 text-sm">
          평가 중 오류가 발생했습니다. 재평가를 시도해주세요.
        </div>
      )}

      {/* Documents */}
      <div className="bg-white p-5 rounded-lg shadow-sm">
        <h3 className="font-semibold text-gray-900 mb-3">제출 서류</h3>
        {candidate.documents.length === 0 ? (
          <p className="text-gray-400 text-sm">서류 없음</p>
        ) : (
          <ul className="space-y-2">
            {candidate.documents.map((doc) => (
              <li
                key={doc.id}
                className="flex items-center gap-3 text-sm text-gray-700"
              >
                <span className="px-2 py-0.5 bg-gray-100 rounded text-xs font-mono uppercase">
                  {doc.file_type}
                </span>
                <span>{doc.filename}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Evaluation */}
      {latestEval && (
        <>
          <div className="bg-white p-5 rounded-lg shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">점수 레이더</h3>
            <ScoreRadar scores={latestEval.scores} />
          </div>

          <EvaluationReport evaluation={latestEval} />
        </>
      )}
    </div>
  );
}
