"use client";

import { CandidateListItem } from "@/lib/api";

const statusLabels: Record<string, { text: string; color: string }> = {
  pending: { text: "대기", color: "bg-gray-100 text-gray-700" },
  evaluating: { text: "평가중", color: "bg-blue-100 text-blue-700" },
  completed: { text: "완료", color: "bg-green-100 text-green-700" },
  error: { text: "오류", color: "bg-red-100 text-red-700" },
};

const recLabels: Record<string, { text: string; color: string }> = {
  통과: { text: "통과", color: "bg-green-100 text-green-800" },
  검토: { text: "검토", color: "bg-yellow-100 text-yellow-800" },
  탈락: { text: "탈락", color: "bg-red-100 text-red-800" },
};

export default function CandidateTable({
  candidates,
}: {
  candidates: CandidateListItem[];
}) {
  if (candidates.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">등록된 후보가 없습니다</p>
        <p className="text-sm mt-1">
          <a href="/upload" className="text-blue-600 hover:underline">
            새 후보 업로드
          </a>
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full bg-white rounded-lg shadow-sm overflow-hidden">
        <thead>
          <tr className="bg-gray-900 text-white text-sm">
            <th className="text-left px-5 py-3 font-medium">기업/브랜드명</th>
            <th className="text-left px-5 py-3 font-medium">상태</th>
            <th className="text-left px-5 py-3 font-medium">종합 점수</th>
            <th className="text-left px-5 py-3 font-medium">판정</th>
            <th className="text-left px-5 py-3 font-medium">등록일</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((c) => {
            const status = statusLabels[c.status] || statusLabels.pending;
            const rec = c.recommendation
              ? recLabels[c.recommendation]
              : null;
            return (
              <tr
                key={c.id}
                className="border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition-colors"
                onClick={() => (window.location.href = `/candidates/${c.id}`)}
              >
                <td className="px-5 py-4 font-medium text-gray-900">
                  {c.name}
                </td>
                <td className="px-5 py-4">
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-medium ${status.color}`}
                  >
                    {status.text}
                  </span>
                </td>
                <td className="px-5 py-4">
                  {c.latest_score !== null ? (
                    <span className="font-semibold text-gray-900">
                      {c.latest_score}점
                    </span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-5 py-4">
                  {rec ? (
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium ${rec.color}`}
                    >
                      {rec.text}
                    </span>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
                <td className="px-5 py-4 text-gray-500 text-sm">
                  {new Date(c.created_at).toLocaleDateString("ko-KR")}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
