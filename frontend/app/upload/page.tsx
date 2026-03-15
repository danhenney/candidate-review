"use client";

import { useState } from "react";
import UploadForm from "@/components/UploadForm";
import { api } from "@/lib/api";

export default function InputPage() {
  const [excelLoading, setExcelLoading] = useState(false);
  const [excelResult, setExcelResult] = useState<string | null>(null);

  const handleExcelImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setExcelLoading(true);
    setExcelResult(null);

    try {
      const result = await api.import.excel(file);
      setExcelResult(`${result.count}개 후보 가져오기 완료`);
    } catch (err) {
      setExcelResult(
        `오류: ${err instanceof Error ? err.message : "알 수 없는 오류"}`
      );
    } finally {
      setExcelLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">서류 입력</h1>
        <p className="text-gray-500 mt-1">
          지원자 서류를 업로드하여 AI 평가를 시작합니다
        </p>
      </div>

      {/* Individual upload */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          개별 업로드
        </h2>
        <UploadForm />
      </div>

      {/* Excel bulk import */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          엑셀 일괄 가져오기
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          나인하이어 등에서 내보낸 엑셀 파일을 업로드합니다
        </p>

        <label className="block">
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleExcelImport}
            disabled={excelLoading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 disabled:opacity-50"
          />
        </label>

        {excelLoading && (
          <p className="mt-3 text-sm text-blue-600">처리 중...</p>
        )}
        {excelResult && (
          <div
            className={`mt-3 p-3 rounded-lg text-sm ${
              excelResult.startsWith("오류")
                ? "bg-red-50 text-red-700"
                : "bg-green-50 text-green-700"
            }`}
          >
            {excelResult}
          </div>
        )}
      </div>
    </div>
  );
}
