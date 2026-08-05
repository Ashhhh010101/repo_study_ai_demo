import { useEffect, useMemo, useState } from "react";

import { apiClient } from "../api/client";
import AppHeader from "../components/AppHeader";
import ChatPanel from "../components/ChatPanel";
import ErrorBox from "../components/ErrorBox";
import FileTree from "../components/FileTree";
import Icon from "../components/Icon";
import LoadingState from "../components/LoadingState";
import ReportViewer from "../components/ReportViewer";
import { useApiKey } from "../context/ApiKeyContext";
import { AppLink } from "../context/RouterContext";
import type { FileTreeNode, RepoAnalysis, RepoFile, RepoProject } from "../types/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}

export default function RepoReport({ projectId }: { projectId: string }) {
  const { apiKey, setApiKey, clearApiKey } = useApiKey();
  const [showKey, setShowKey] = useState(false);
  const [project, setProject] = useState<RepoProject | null>(null);
  const [report, setReport] = useState<RepoAnalysis | null>(null);
  const [files, setFiles] = useState<RepoFile[]>([]);
  const [tree, setTree] = useState<FileTreeNode[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [model, setModel] = useState("gemini-2.5-flash");
  const accessToken = sessionStorage.getItem(`repo-study-ai-project:${projectId}`) ?? "";

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      if (!accessToken) {
        setError("This report link is missing its temporary access token. Start a new analysis in this tab.");
        setLoading(false);
        return;
      }
      try {
        const [projectData, reportData, filesData] = await Promise.all([
          apiClient.getProject(projectId, accessToken),
          apiClient.getReport(projectId, accessToken),
          apiClient.getFiles(projectId, accessToken)
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
        setError(err instanceof Error ? err.message : "Unexpected report error.");
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
  }, [accessToken, projectId]);

  const languageCount = useMemo(
    () => new Set(files.map((file) => file.language).filter(Boolean)).size,
    [files]
  );

  if (loading) {
    return (
      <div className="app-shell min-h-screen">
        <AppHeader />
        <main className="relative z-10 mx-auto max-w-2xl px-5 py-24 sm:px-8">
          <LoadingState
            title="Loading repository intelligence"
            detail="Fetching project metadata, the architecture brief, and the ranked repository surface."
          />
        </main>
      </div>
    );
  }

  if (error || !project || !report) {
    return (
      <div className="app-shell min-h-screen">
        <AppHeader />
        <main className="relative z-10 mx-auto max-w-2xl px-5 py-24 sm:px-8">
          <ErrorBox message={error ?? "Project not found."} />
          <AppLink
            to="/"
            className="mt-5 inline-flex items-center gap-2 text-xs font-medium text-ink-soft hover:text-ink"
          >
            <Icon name="back" size={15} />
            Return to analyzer
          </AppLink>
        </main>
      </div>
    );
  }

  async function handleAsk(message: string) {
    return apiClient.askQuestion(projectId, accessToken, {
      message,
      gemini_api_key: apiKey
      , model
    });
  }

  const stackEntries = Object.entries(report.tech_stack_json).flatMap(([group, values]) =>
    values.map((value) => ({ group, value }))
  );

  return (
    <div className="app-shell min-h-screen">
      <AppHeader />
      <main className="relative z-10 mx-auto max-w-[1440px] px-5 pb-16 pt-7 sm:px-8">
        <AppLink
          to="/"
          className="mb-5 inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.13em] text-muted transition hover:text-ink"
        >
          <Icon name="back" size={14} />
          New analysis
        </AppLink>

        <section className="surface-card overflow-hidden">
          <div className="flex flex-col gap-7 p-6 sm:p-8 lg:flex-row lg:items-end lg:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <span className="eyebrow">Analysis #{project.id}</span>
                <span className="rounded-md border border-accent/20 bg-accent/[0.05] px-2 py-1 font-mono text-[8px] uppercase tracking-[0.14em] text-accent">
                  {project.status}
                </span>
              </div>
              <h1 className="mt-4 truncate text-3xl font-semibold tracking-[-0.035em] text-ink sm:text-4xl">
                {project.repo_name}
              </h1>
              <a
                href={project.repo_url}
                target="_blank"
                rel="noreferrer"
                className="mt-3 inline-flex max-w-full items-center gap-2 font-mono text-[11px] text-muted transition hover:text-cyan"
              >
                <Icon name="github" size={14} className="shrink-0" />
                <span className="truncate">{project.repo_url.replace("https://github.com/", "")}</span>
              </a>
            </div>
            <div className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-line bg-line lg:min-w-[410px]">
              {[
                ["Scanned", files.length.toLocaleString(), "files"],
                ["Detected", languageCount.toLocaleString(), "languages"],
                ["Branch", project.branch ?? "default", "ref"]
              ].map(([label, value, suffix]) => (
                <div key={label} className="min-w-0 bg-canvas/80 px-4 py-3">
                  <div className="font-mono text-[8px] uppercase tracking-[0.14em] text-muted">{label}</div>
                  <div className="mt-1 truncate text-sm font-semibold text-ink" title={value}>
                    {value}
                  </div>
                  <div className="mt-0.5 font-mono text-[8px] text-muted">{suffix}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 border-t border-line bg-canvas/45 px-6 py-3 sm:px-8">
            {stackEntries.length ? (
              stackEntries.slice(0, 18).map(({ group, value }) => (
                <span
                  key={`${group}-${value}`}
                  className="rounded-md border border-line bg-panel px-2 py-1 font-mono text-[9px] text-ink-soft"
                >
                  <span className="text-muted">{group}/</span>
                  {value}
                </span>
              ))
            ) : (
              <span className="font-mono text-[9px] text-muted">No stack metadata detected</span>
            )}
            <span className="ml-auto hidden font-mono text-[8px] uppercase tracking-[0.1em] text-muted sm:block">
              generated {formatDate(project.updated_at)}
            </span>
          </div>
        </section>

        <section className="mt-5 grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_390px]">
          <div className="min-w-0 space-y-5">
            <ReportViewer markdown={report.generated_report_markdown} />
            <FileTree files={files} tree={tree} />
          </div>

          <aside className="space-y-5 xl:sticky xl:top-5">
            <section className="surface-card overflow-hidden">
              <div className="flex items-center justify-between border-b border-line px-5 py-4">
                <div className="flex items-center gap-2">
                  <Icon name="key" size={15} className="text-accent" />
                  <h2 className="text-xs font-semibold text-ink">Provider key</h2>
                </div>
                <span className="font-mono text-[8px] uppercase tracking-[0.12em] text-muted">
                  volatile memory
                </span>
              </div>
              <div className="p-4">
                <div className="relative">
                  <input
                    value={apiKey}
                    onChange={(event) => setApiKey(event.target.value)}
                    type={showKey ? "text" : "password"}
                    placeholder="Paste key to enable repository Q&A"
                    className="field-input pr-20"
                    autoComplete="new-password"
                    autoCapitalize="none"
                    autoCorrect="off"
                    spellCheck={false}
                    maxLength={512}
                  />
                  <div className="absolute right-1 top-1 flex">
                    <button
                      type="button"
                      onClick={() => setShowKey((current) => !current)}
                      className="grid h-9 w-9 place-items-center rounded-md text-muted transition hover:bg-panel-soft hover:text-ink"
                      aria-label={showKey ? "Hide API key" : "Show API key"}
                    >
                      <Icon name={showKey ? "eyeOff" : "eye"} size={15} />
                    </button>
                    {apiKey ? (
                      <button
                        type="button"
                        onClick={clearApiKey}
                        className="h-9 rounded-md px-2 text-[9px] font-medium uppercase tracking-[0.08em] text-danger transition hover:bg-danger/[0.06]"
                      >
                        Clear
                      </button>
                    ) : null}
                  </div>
                </div>
                <p className="mt-2.5 flex items-start gap-2 text-[10px] leading-4 text-muted">
                  <Icon name="shield" size={13} className="mt-0.5 shrink-0 text-accent" />
                  Never persisted. Refreshing this tab clears it; code excerpts are sent to Gemini only when needed.
                </p>
              </div>
            </section>
            <ChatPanel geminiApiKey={apiKey} onAsk={handleAsk} />
          </aside>
        </section>
      </main>
    </div>
  );
}
