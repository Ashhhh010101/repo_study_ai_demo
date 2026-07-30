import { FormEvent, useState } from "react";

import Icon from "./Icon";

type RepoInputProps = {
  onSubmit: (payload: {
    repo_url: string;
    branch?: string;
    commit?: string;
    gemini_api_key: string;
  }) => Promise<void>;
  loading: boolean;
};

export default function RepoInput({ onSubmit, loading }: RepoInputProps) {
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("");
  const [commit, setCommit] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!acknowledged) {
      return;
    }
    await onSubmit({
      repo_url: repoUrl.trim(),
      branch: branch.trim() || undefined,
      commit: commit.trim() || undefined,
      gemini_api_key: apiKey.trim()
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="overflow-hidden rounded-2xl border border-line bg-panel/95 shadow-panel backdrop-blur"
    >
      <div className="flex items-start justify-between border-b border-line px-6 py-5 sm:px-7">
        <div>
          <div className="flex items-center gap-2">
            <Icon name="spark" size={16} className="text-accent" />
            <h2 className="text-sm font-semibold text-ink">Start an analysis</h2>
          </div>
          <p className="mt-1.5 text-xs leading-5 text-muted">Map a public GitHub repository.</p>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label htmlFor="commit" className="field-label">Commit</label>
            <span className="font-mono text-[9px] uppercase tracking-[0.12em] text-muted">optional</span>
          </div>
          <input id="commit" value={commit} onChange={(event) => setCommit(event.target.value)}
            placeholder="full or abbreviated commit SHA" className="field-input font-mono" maxLength={40}
            autoCapitalize="none" autoCorrect="off" spellCheck={false} disabled={loading} />
        </div>
        <span className="rounded-md border border-cyan/20 bg-cyan/5 px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] text-cyan">
          Gemini · BYOK
        </span>
      </div>

      <div className="space-y-5 p-6 sm:p-7">
        <div>
          <label htmlFor="repo-url" className="field-label">
            Repository URL
          </label>
          <div className="field-wrap">
            <Icon name="github" size={17} className="field-icon" />
            <input
              id="repo-url"
              value={repoUrl}
              onChange={(event) => setRepoUrl(event.target.value)}
              placeholder="https://github.com/owner/repository"
              className="field-input pl-10"
              type="url"
              inputMode="url"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              disabled={loading}
              pattern="https://github\.com/[^/]+/[^/]+/?"
              required
            />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label htmlFor="api-key" className="field-label">
              Gemini API key
            </label>
            <span className="flex items-center gap-1 font-mono text-[9px] uppercase tracking-[0.12em] text-accent">
              <Icon name="lock" size={11} />
              memory only
            </span>
          </div>
          <div className="field-wrap">
            <Icon name="key" size={17} className="field-icon" />
            <input
              id="api-key"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="Paste a restricted provider key"
              type={showKey ? "text" : "password"}
              className="field-input px-10"
              autoComplete="new-password"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              disabled={loading}
              required
              minLength={10}
              maxLength={512}
            />
            <button
              type="button"
              onClick={() => setShowKey((current) => !current)}
              className="absolute right-1 top-1 grid h-9 w-9 place-items-center rounded-md text-muted transition hover:bg-panel-soft hover:text-ink"
              aria-label={showKey ? "Hide API key" : "Show API key"}
            >
              <Icon name={showKey ? "eyeOff" : "eye"} size={16} />
            </button>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label htmlFor="branch" className="field-label">
              Branch
            </label>
            <span className="font-mono text-[9px] uppercase tracking-[0.12em] text-muted">optional</span>
          </div>
          <div className="field-wrap">
            <Icon name="branch" size={17} className="field-icon" />
            <input
              id="branch"
              value={branch}
              onChange={(event) => setBranch(event.target.value)}
              placeholder="default branch"
              className="field-input pl-10"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              disabled={loading}
              maxLength={255}
            />
          </div>
        </div>

        <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-line bg-canvas/60 p-3.5">
          <input
            type="checkbox"
            checked={acknowledged}
            onChange={(event) => setAcknowledged(event.target.checked)}
            disabled={loading}
            className="mt-0.5 h-4 w-4 shrink-0 accent-[#9dfc75]"
            required
          />
          <span className="text-[11px] leading-5 text-muted">
            I understand that selected public repository content is sent to Gemini for analysis. My key is sent only
            in the request header, held transiently in browser/backend memory, never written to storage or logs, and
            discarded when the request/UI session ends or I clear it. Provider retention and billing policies still apply.
          </span>
        </label>

        <button
          type="submit"
          disabled={loading || !acknowledged}
          className="group flex h-12 w-full items-center justify-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-[#071006] transition hover:bg-accent-bright disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? (
            <>
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-[#071006]/25 border-t-[#071006]" />
              Processing repository
            </>
          ) : (
            <>
              Analyze codebase
              <Icon name="arrow" size={17} className="transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-3 border-t border-line bg-canvas/50">
        {[
          ["Key", "volatile"],
          ["Index", "local"],
          ["Clone", "shallow"]
        ].map(([label, value], index) => (
          <div key={label} className={`px-3 py-3 text-center ${index ? "border-l border-line" : ""}`}>
            <div className="font-mono text-[8px] uppercase tracking-[0.16em] text-muted">{label}</div>
            <div className="mt-0.5 font-mono text-[10px] text-ink-soft">{value}</div>
          </div>
        ))}
      </div>
    </form>
  );
}
