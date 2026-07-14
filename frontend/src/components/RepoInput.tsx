import { FormEvent, useState } from "react";

type RepoInputProps = {
  onSubmit: (payload: { repo_url: string; branch?: string; gemini_api_key: string }) => Promise<void>;
  loading: boolean;
};

export default function RepoInput({ onSubmit, loading }: RepoInputProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [apiKey, setApiKey] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onSubmit({
      repo_url: repoUrl.trim(),
      branch: branch.trim() || undefined,
      gemini_api_key: apiKey.trim()
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-[2rem] border border-stone-200 bg-white/90 p-8 shadow-panel">
      <div>
        <label className="mb-2 block text-sm font-semibold text-ink">Public GitHub repo URL</label>
        <input
          value={repoUrl}
          onChange={(event) => setRepoUrl(event.target.value)}
          placeholder="https://github.com/owner/repo"
          className="w-full rounded-2xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-ember"
          required
        />
      </div>
      <div>
        <label className="mb-2 block text-sm font-semibold text-ink">Gemini API key</label>
        <input
          value={apiKey}
          onChange={(event) => setApiKey(event.target.value)}
          placeholder="AIza..."
          type="password"
          className="w-full rounded-2xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-ember"
          required
        />
      </div>
      <div>
        <label className="mb-2 block text-sm font-semibold text-ink">Branch (optional)</label>
        <input
          value={branch}
          onChange={(event) => setBranch(event.target.value)}
          placeholder="main"
          className="w-full rounded-2xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-ember"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? "Analyzing repository..." : "Analyze repository"}
      </button>
    </form>
  );
}
