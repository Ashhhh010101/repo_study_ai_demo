import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { apiClient } from "../api/client";
import ErrorBox from "../components/ErrorBox";
import LoadingState from "../components/LoadingState";
import RepoInput from "../components/RepoInput";

export default function Home() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("Ready to clone, scan, index, and summarize a public repository.");
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(payload: { repo_url: string; branch?: string; gemini_api_key: string }) {
    setLoading(true);
    setError(null);
    setStatusMessage("Cloning repository and building grounded repo context...");
    try {
      const result = await apiClient.analyzeRepo(payload);
      navigate(`/projects/${result.project_id}`, {
        state: { geminiApiKey: payload.gemini_api_key }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
      setStatusMessage("Ready to clone, scan, index, and summarize a public repository.");
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-7xl flex-col px-6 py-10 lg:px-10">
      <section className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-[2.5rem] bg-ink px-8 py-10 text-sand shadow-panel">
          <p className="text-sm uppercase tracking-[0.3em] text-amber-200">localhost-first mvp</p>
          <h1 className="mt-4 font-display text-5xl leading-tight">
            Understand a GitHub repo before you read every file.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-7 text-stone-200">
            This tool clones a public repository locally, builds structured repo context, generates an onboarding report,
            and then lets you ask repo-grounded questions with cited file references.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-white/10 p-4">
              <div className="text-sm font-semibold text-amber-100">1. Analyze</div>
              <p className="mt-2 text-sm text-stone-200">Clone, scan, detect stack, rank files, and chunk code.</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4">
              <div className="text-sm font-semibold text-amber-100">2. Report</div>
              <p className="mt-2 text-sm text-stone-200">Generate a structured onboarding report grounded in repo evidence.</p>
            </div>
            <div className="rounded-2xl bg-white/10 p-4">
              <div className="text-sm font-semibold text-amber-100">3. Ask</div>
              <p className="mt-2 text-sm text-stone-200">Use retrieved repo chunks plus the stored report to answer questions.</p>
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <RepoInput onSubmit={handleAnalyze} loading={loading} />
          {loading ? <LoadingState title="Repository analysis in progress" detail={statusMessage} /> : null}
          {error ? <ErrorBox message={error} /> : null}
        </div>
      </section>
    </main>
  );
}
