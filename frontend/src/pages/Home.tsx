import { useState } from "react";

import { apiClient } from "../api/client";
import AppHeader from "../components/AppHeader";
import ErrorBox from "../components/ErrorBox";
import Icon from "../components/Icon";
import LoadingState from "../components/LoadingState";
import RepoInput from "../components/RepoInput";
import { useApiKey } from "../context/ApiKeyContext";
import { useRouter } from "../context/RouterContext";

const pipeline = [
  { command: "git clone --depth 1", detail: "public repository" },
  { command: "scan + rank", detail: "structure and key files" },
  { command: "index", detail: "line-aware code chunks" },
  { command: "reason", detail: "grounded architecture report" }
];

const capabilities = [
  {
    icon: "terminal" as const,
    title: "Trace the system",
    text: "Map entrypoints, request paths, data flow, and subsystem boundaries from repository evidence."
  },
  {
    icon: "branch" as const,
    title: "Prioritize the code",
    text: "Rank important files and generate a reading order instead of treating every file equally."
  },
  {
    icon: "shield" as const,
    title: "Keep key custody",
    text: "Bring a restricted Gemini key. It stays in volatile UI memory and is never written to app storage."
  }
];

export default function Home() {
  const { navigate } = useRouter();
  const { setApiKey } = useApiKey();
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(
    "Cloning, scanning, indexing, and building your architecture brief."
  );
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(payload: {
    repo_url: string;
    branch?: string;
    gemini_api_key: string;
  }) {
    setLoading(true);
    setError(null);
    setStatusMessage("Building a grounded map of the repository. Large codebases can take a few minutes.");
    try {
      const result = await apiClient.analyzeRepo(payload);
      setApiKey(payload.gemini_api_key);
      navigate(`/projects/${result.project_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected analysis error.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell min-h-screen overflow-hidden">
      <AppHeader />
      <main className="relative z-10 mx-auto max-w-[1440px] px-5 pb-16 pt-12 sm:px-8 lg:pt-20">
        <section className="grid items-center gap-12 xl:grid-cols-[minmax(0,1.08fr)_minmax(420px,0.78fr)] xl:gap-20">
          <div>
            <div className="eyebrow">
              <span className="h-1.5 w-1.5 rounded-full bg-accent shadow-glow" />
              Open-source repository intelligence
            </div>
            <h1 className="mt-6 max-w-4xl text-balance text-5xl font-semibold leading-[1.02] tracking-[-0.045em] text-ink sm:text-6xl lg:text-7xl">
              See the system
              <br />
              <span className="text-gradient">inside the source.</span>
            </h1>
            <p className="mt-7 max-w-2xl text-pretty text-base leading-7 text-muted sm:text-lg sm:leading-8">
              Turn an unfamiliar GitHub repository into an evidence-backed architecture map, prioritized reading
              path, and code-grounded Q&amp;A workspace.
            </p>

            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3">
              {["Local-first index", "Public repos only", "BYOK Gemini"].map((item) => (
                <span key={item} className="flex items-center gap-2 text-xs font-medium text-ink-soft">
                  <Icon name="check" size={15} className="text-accent" />
                  {item}
                </span>
              ))}
            </div>

            <div className="mt-12 max-w-2xl overflow-hidden rounded-xl border border-line bg-[#080c12]/90 shadow-panel">
              <div className="flex h-10 items-center justify-between border-b border-line px-4">
                <div className="flex gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#fb7185]/70" />
                  <span className="h-2 w-2 rounded-full bg-[#fbbf24]/70" />
                  <span className="h-2 w-2 rounded-full bg-accent/70" />
                </div>
                <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted">
                  analysis.pipeline
                </span>
              </div>
              <div className="grid gap-px bg-line sm:grid-cols-2">
                {pipeline.map((item, index) => (
                  <div key={item.command} className="group bg-[#080c12] px-4 py-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-[10px] text-accent/70">0{index + 1}</span>
                      <span className="font-mono text-xs text-ink">{item.command}</span>
                    </div>
                    <p className="mt-1 pl-8 text-[11px] text-muted">{item.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-10 -z-10 bg-[radial-gradient(circle,rgba(157,252,117,0.09),transparent_65%)]" />
            <RepoInput onSubmit={handleAnalyze} loading={loading} />
            <div className="mt-4 space-y-4" aria-live="polite">
              {loading ? <LoadingState title="Analysis pipeline running" detail={statusMessage} /> : null}
              {error ? <ErrorBox message={error} /> : null}
            </div>
          </div>
        </section>

        <section className="mt-24 border-t border-line pt-10 lg:mt-32">
          <div className="mb-8 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
            <div>
              <p className="eyebrow">Designed for orientation</p>
              <h2 className="mt-4 text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
                From clone to mental model.
              </h2>
            </div>
            <p className="max-w-md text-sm leading-6 text-muted">
              The report stays tied to concrete file paths and retrieved code, so unknowns remain visible.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {capabilities.map((capability) => (
              <article
                key={capability.title}
                className="group rounded-xl border border-line bg-panel/75 p-6 transition duration-300 hover:-translate-y-0.5 hover:border-accent/25 hover:bg-panel"
              >
                <div className="grid h-10 w-10 place-items-center rounded-lg border border-line bg-canvas text-accent transition group-hover:border-accent/30">
                  <Icon name={capability.icon} size={19} />
                </div>
                <h3 className="mt-5 text-sm font-semibold text-ink">{capability.title}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">{capability.text}</p>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
