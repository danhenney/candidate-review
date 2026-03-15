"use client";

import { useEffect, useState } from "react";
import { api, CandidateListItem } from "@/lib/api";
import CandidateTable from "@/components/CandidateTable";

export default function SummaryPage() {
  const [candidates, setCandidates] = useState<CandidateListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.candidates
      .list()
      .then(setCandidates)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const completed = candidates.filter((c) => c.status === "completed");
  const avgScore =
    completed.length > 0
      ? Math.round(
          completed.reduce((sum, c) => sum + (c.latest_score || 0), 0) /
            completed.length
        )
      : 0;
  const passCount = completed.filter((c) => c.recommendation === "통과").length;
  const reviewCount = completed.filter(
    (c) => c.recommendation === "검토"
  ).length;
  const failCount = completed.filter((c) => c.recommendation === "탈락").length;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">전체 요약</h1>
        <p className="text-gray-500 mt-1">평가 완료된 모든 후보 현황</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-white p-5 rounded-lg shadow-sm text-center">
          <p className="text-3xl font-bold text-gray-900">
            {candidates.length}
          </p>
          <p className="text-sm text-gray-500 mt-1">전체 후보</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm text-center">
          <p className="text-3xl font-bold text-blue-600">{avgScore}점</p>
          <p className="text-sm text-gray-500 mt-1">평균 점수</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm text-center">
          <p className="text-3xl font-bold text-green-600">{passCount}</p>
          <p className="text-sm text-gray-500 mt-1">통과</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm text-center">
          <p className="text-3xl font-bold text-yellow-600">{reviewCount}</p>
          <p className="text-sm text-gray-500 mt-1">검토</p>
        </div>
        <div className="bg-white p-5 rounded-lg shadow-sm text-center">
          <p className="text-3xl font-bold text-red-600">{failCount}</p>
          <p className="text-sm text-gray-500 mt-1">탈락</p>
        </div>
      </div>

      {loading ? (
        <p className="text-gray-500 text-center py-8">불러오는 중...</p>
      ) : (
        <CandidateTable candidates={candidates} />
      )}
    </div>
  );
}
