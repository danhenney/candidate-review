"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { api } from "@/lib/api";

export default function UploadForm() {
  const [name, setName] = useState("");
  const [notes, setNotes] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        [".pptx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    if (files.length === 0) return;

    setLoading(true);
    setResult(null);

    try {
      // 1. Create candidate
      const candidate = await api.candidates.create({
        name: name.trim(),
        notes: notes.trim(),
      });

      // 2. Upload documents
      await api.documents.upload(candidate.id, files);

      // 3. Trigger evaluation
      await api.evaluations.trigger(candidate.id);

      setResult(`"${name}" 등록 완료! 평가가 시작되었습니다.`);
      setName("");
      setNotes("");
      setFiles([]);

      // Redirect after short delay
      setTimeout(() => {
        window.location.href = `/candidates/${candidate.id}`;
      }, 1500);
    } catch (err) {
      setResult(`오류: ${err instanceof Error ? err.message : "알 수 없는 오류"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          기업/브랜드명 *
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="예: 브랜드명"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          메모 (선택)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
          placeholder="추가 참고 사항"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          제출 서류 *
        </label>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />
          <p className="text-gray-600">
            {isDragActive
              ? "여기에 파일을 놓으세요"
              : "파일을 드래그하거나 클릭하여 업로드"}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            PDF, PPTX, XLSX 지원
          </p>
        </div>

        {files.length > 0 && (
          <ul className="mt-3 space-y-1">
            {files.map((f, i) => (
              <li
                key={i}
                className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded text-sm"
              >
                <span className="text-gray-700">{f.name}</span>
                <button
                  type="button"
                  onClick={() => setFiles(files.filter((_, j) => j !== i))}
                  className="text-red-500 hover:text-red-700"
                >
                  삭제
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button
        type="submit"
        disabled={loading || !name.trim() || files.length === 0}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? "처리 중..." : "등록 및 평가 시작"}
      </button>

      {result && (
        <div
          className={`p-4 rounded-lg text-sm ${
            result.startsWith("오류")
              ? "bg-red-50 text-red-700"
              : "bg-green-50 text-green-700"
          }`}
        >
          {result}
        </div>
      )}
    </form>
  );
}
