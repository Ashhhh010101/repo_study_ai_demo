import type {
  AnalyzeResponse,
  ChatRequest,
  ChatResponse,
  RepoAnalysis,
  RepoAnalyzeRequest,
  RepoFile,
  RepoFilesResponse,
  RepoProject
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  analyzeRepo(payload: RepoAnalyzeRequest) {
    return request<AnalyzeResponse>("/api/repos/analyze", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  getProject(projectId: string) {
    return request<RepoProject>(`/api/repos/${projectId}`);
  },
  getReport(projectId: string) {
    return request<RepoAnalysis>(`/api/repos/${projectId}/report`);
  },
  getFiles(projectId: string) {
    return request<RepoFilesResponse>(`/api/repos/${projectId}/files`);
  },
  askQuestion(projectId: string, payload: ChatRequest) {
    return request<ChatResponse>(`/api/chat/${projectId}`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
};
