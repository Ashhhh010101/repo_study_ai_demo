export type RepoAnalyzeRequest = {
  repo_url: string;
  branch?: string;
  commit?: string;
  gemini_api_key: string;
};

export type RepoFile = {
  id: number;
  path: string;
  language: string | null;
  file_type: string | null;
  size_bytes: number;
  importance_score: number;
};

export type FileTreeNode = {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FileTreeNode[];
};

export type RepoFilesResponse = {
  files: RepoFile[];
  tree: FileTreeNode[];
};

export type RepoProject = {
  id: number;
  repo_url: string;
  repo_name: string;
  branch: string | null;
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export type RepoAnalysis = {
  project_id: number;
  overview: string;
  tech_stack_json: Record<string, string[]>;
  architecture_summary: string;
  folder_summary_json: Record<string, unknown>;
  important_files_json: Array<Record<string, unknown>>;
  request_flow: string;
  data_flow: string;
  setup_instructions: string;
  reading_order_json: Array<Record<string, unknown> | string>;
  risks: string;
  generated_report_markdown: string;
};

export type AnalyzeResponse = {
  project_id: number;
  status: string;
  report: RepoAnalysis;
};

export type ChatRequest = {
  message: string;
  gemini_api_key: string;
};

export type ChatResponse = {
  answer: string;
  used_chunks: Array<Record<string, unknown>>;
};
