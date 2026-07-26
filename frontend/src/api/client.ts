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

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function getErrorMessage(response: Response): Promise<string> {
  if (response.status >= 500) {
    return "The analysis service failed unexpectedly. Check the backend logs and try again.";
  }

  try {
    const data = (await response.json()) as {
      detail?: string | Array<{ msg?: string }>;
    };
    if (typeof data.detail === "string") {
      return data.detail;
    }
    if (Array.isArray(data.detail)) {
      const messages = data.detail.flatMap((item) => (item.msg ? [item.msg] : []));
      if (messages.length) {
        return messages.join(" ");
      }
    }
  } catch {
    // Fall through to the status-based message without exposing raw upstream HTML.
  }
  return `Request failed with status ${response.status}.`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    credentials: "omit",
    referrerPolicy: "no-referrer",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
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
    return request<RepoProject>(`/api/repos/${encodeURIComponent(projectId)}`);
  },
  getReport(projectId: string) {
    return request<RepoAnalysis>(`/api/repos/${encodeURIComponent(projectId)}/report`);
  },
  getFiles(projectId: string) {
    return request<RepoFilesResponse>(`/api/repos/${encodeURIComponent(projectId)}/files`);
  },
  askQuestion(projectId: string, payload: ChatRequest) {
    return request<ChatResponse>(`/api/chat/${encodeURIComponent(projectId)}`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
};
