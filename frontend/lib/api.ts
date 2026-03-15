const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "요청 실패");
  }
  return res.json();
}

export interface CandidateListItem {
  id: number;
  name: string;
  status: string;
  created_at: string;
  latest_score: number | null;
  recommendation: string | null;
}

export interface Candidate {
  id: number;
  name: string;
  notes: string;
  status: string;
  created_at: string;
  updated_at: string;
  documents: Document[];
  evaluations: Evaluation[];
}

export interface Document {
  id: number;
  candidate_id: number;
  filename: string;
  file_type: string;
  created_at: string;
}

export interface Evaluation {
  id: number;
  candidate_id: number;
  overall_score: number | null;
  scores: Record<string, { score: number; max: number; reasoning: string }>;
  summary: string;
  recommendation: string;
  strengths: string[];
  risks: string[];
  model_used: string;
  tokens_used: number;
  created_at: string;
}

export const api = {
  candidates: {
    list: () => request<CandidateListItem[]>("/candidates"),
    get: (id: number) => request<Candidate>(`/candidates/${id}`),
    create: (data: { name: string; notes?: string }) =>
      request<Candidate>("/candidates", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    delete: (id: number) =>
      request(`/candidates/${id}`, { method: "DELETE" }),
  },
  documents: {
    upload: async (candidateId: number, files: File[]) => {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      const res = await fetch(`${API_BASE}/candidates/${candidateId}/documents`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("업로드 실패");
      return res.json();
    },
  },
  evaluations: {
    trigger: (candidateId: number) =>
      request(`/candidates/${candidateId}/evaluate`, { method: "POST" }),
  },
  import: {
    excel: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/import/excel`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("가져오기 실패");
      return res.json();
    },
  },
};
