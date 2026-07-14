import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import ChatPanel from "../components/ChatPanel";
import ErrorBox from "../components/ErrorBox";
import FileTree from "../components/FileTree";
import LoadingState from "../components/LoadingState";
import ReportViewer from "../components/ReportViewer";
import type { FileTreeNode, RepoAnalysis, RepoFile, RepoProject } from "../types/api";

type LocationState = {
  geminiApiKey?: string;
};

export default function RepoReport() {
  const { projectId = "" } = useParams();
  const location = useLocation();
  const state = (location.state as LocationState | null) ?? null;
  const [project, setProject] = useState<RepoProject | null>(null);
  const [report, setReport] = useState<RepoAnalysis | null>(null);
  const [files, setFiles] = useState<RepoFile[]>([]);
  const [tree, setTree] = useState<FileTreeNode[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [geminiApiKey, setGeminiApiKey] = useState(state?.geminiApiKey ?? "");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [projectData, reportData, filesData] = await Promise.all([
          apiClient.getProject(projectId),
          apiClient.getReport(projectId),
          apiClient.getFiles(projectId)
        ]);
        if (!active) {
          return;
        }
        setProject(projectData);
        setReport(reportData);
        setFiles(filesData.files);
        setTree(filesData.tree);
      } catch (err) {
        if (!active) {
          return;
        }
        setError(err instanceof Error ? err.message : "Unexpected error");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [projectId]);

  if (loading) {
    return (
      <main className="mx-auto max-w-7xl px-6 py-10">
        <LoadingState title="Loading analyzed repository" detail="Fetching project metadata, report, and scanned file list." />
      </main>
    );
  }

  if (error || !project || !report) {
    return (
      <main className="mx-auto max-w-7xl px-6 py-10">
        <ErrorBox message={error ?? "Project not found"} />
      </main>
    );
  }

  async function handleAsk(message: string) {
    return apiClient.askQuestion(projectId, {
      message,
      gemini_api_key: geminiApiKey
    });
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-10">
      <section className="rounded-[2.5rem] bg-white/80 p-8 shadow-panel">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-ember">Repository report</p>
            <h1 className="mt-3 font-display text-4xl text-ink">{project.repo_name}</h1>
            <p className="mt-2 text-sm text-slate">{project.repo_url}</p>
          </div>
          <div className="max-w-md">
            <label className="mb-2 block text-sm font-semibold text-ink">Gemini API key for follow-up chat</label>
            <input
              value={geminiApiKey}
              onChange={(event) => setGeminiApiKey(event.target.value)}
              type="password"
              placeholder="Paste again for Q&A if needed"
              className="w-full rounded-2xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-ember"
            />
          </div>
        </div>
        <div className="mt-6 flex flex-wrap gap-2">
          {Object.entries(report.tech_stack_json).flatMap(([group, values]) =>
            values.map((value) => (
              <span key={`${group}-${value}`} className="rounded-full bg-stone-900 px-3 py-1 text-xs font-medium text-white">
                {group}: {value}
              </span>
            ))
          )}
        </div>
      </section>

      <section className="mt-8 grid gap-8 xl:grid-cols-[1.35fr_0.85fr]">
        <div className="space-y-8">
          <ReportViewer markdown={report.generated_report_markdown} />
          <FileTree files={files} tree={tree} />
        </div>
        <ChatPanel geminiApiKey={geminiApiKey} onAsk={handleAsk} />
      </section>
    </main>
  );
}
