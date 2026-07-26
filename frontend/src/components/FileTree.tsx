import { useMemo, useState } from "react";

import type { FileTreeNode, RepoFile } from "../types/api";
import Icon from "./Icon";

type FileTreeProps = {
  files: RepoFile[];
  tree: FileTreeNode[];
};

function formatBytes(bytes: number) {
  if (bytes < 1_000) {
    return `${bytes} B`;
  }
  if (bytes < 1_000_000) {
    return `${(bytes / 1_000).toFixed(1)} KB`;
  }
  return `${(bytes / 1_000_000).toFixed(1)} MB`;
}

function TreeNode({ node, depth = 0 }: { node: FileTreeNode; depth?: number }) {
  if (node.type === "file") {
    return (
      <li className="flex min-w-0 items-center gap-2 py-1.5 text-[11px] text-muted" title={node.path}>
        <Icon name="file" size={13} className="shrink-0 text-muted/70" />
        <span className="truncate">{node.name}</span>
      </li>
    );
  }

  return (
    <li>
      <details open={depth < 1} className="group/tree">
        <summary className="flex cursor-pointer list-none items-center gap-2 py-1.5 text-[11px] font-medium text-ink-soft marker:content-none">
          <Icon
            name="chevron"
            size={12}
            className="shrink-0 text-muted transition-transform group-open/tree:rotate-90"
          />
          <Icon name="folder" size={14} className="shrink-0 text-cyan/75" />
          <span className="truncate">{node.name}</span>
        </summary>
        <ul className="ml-1 border-l border-line pl-4">
          {node.children?.map((child) => (
            <TreeNode key={child.path} node={child} depth={depth + 1} />
          ))}
        </ul>
      </details>
    </li>
  );
}

export default function FileTree({ files, tree }: FileTreeProps) {
  const [view, setView] = useState<"ranked" | "tree">("ranked");
  const [query, setQuery] = useState("");
  const filteredFiles = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return files;
    }
    return files.filter(
      (file) =>
        file.path.toLowerCase().includes(normalized) ||
        file.language?.toLowerCase().includes(normalized) ||
        file.file_type?.toLowerCase().includes(normalized)
    );
  }, [files, query]);

  return (
    <section className="surface-card overflow-hidden">
      <div className="flex flex-col gap-4 border-b border-line px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-7">
        <div>
          <h2 className="text-sm font-semibold text-ink">Repository surface</h2>
          <p className="mt-1 font-mono text-[9px] uppercase tracking-[0.14em] text-muted">
            {files.length.toLocaleString()} scanned files
          </p>
        </div>
        <div className="flex rounded-lg border border-line bg-canvas p-1">
          {(["ranked", "tree"] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setView(tab)}
              className={`rounded-md px-3 py-1.5 text-[10px] font-medium capitalize transition ${
                view === tab ? "bg-panel-soft text-ink shadow-sm" : "text-muted hover:text-ink-soft"
              }`}
            >
              {tab === "ranked" ? "Ranked files" : "File tree"}
            </button>
          ))}
        </div>
      </div>

      {view === "ranked" ? (
        <div>
          <div className="border-b border-line p-4 sm:px-6">
            <div className="relative">
              <Icon name="search" size={15} className="absolute left-3 top-2.5 text-muted" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Filter by path, language, or type"
                className="h-9 w-full rounded-lg border border-line bg-canvas pl-9 pr-3 text-[11px] text-ink outline-none transition placeholder:text-muted/50 focus:border-accent/45"
                type="search"
                spellCheck={false}
              />
            </div>
          </div>
          <div className="max-h-[520px] overflow-auto">
            {filteredFiles.slice(0, 80).map((file, index) => (
              <div
                key={file.id}
                className="grid grid-cols-[2rem_minmax(0,1fr)_auto] items-center gap-3 border-b border-line/70 px-4 py-3 last:border-0 sm:px-6"
              >
                <span className="font-mono text-[9px] text-muted/60">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="min-w-0">
                  <div className="truncate font-mono text-[11px] text-ink-soft" title={file.path}>
                    {file.path}
                  </div>
                  <div className="mt-1 flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.08em] text-muted">
                    <span>{file.language ?? "unknown"}</span>
                    <span className="text-line">/</span>
                    <span>{formatBytes(file.size_bytes)}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-[11px] font-medium text-accent">
                    {file.importance_score.toFixed(1)}
                  </div>
                  <div className="font-mono text-[8px] uppercase tracking-[0.1em] text-muted">rank</div>
                </div>
              </div>
            ))}
            {!filteredFiles.length ? (
              <div className="px-6 py-14 text-center text-xs text-muted">No file matches this filter.</div>
            ) : null}
            {filteredFiles.length > 80 ? (
              <div className="border-t border-line px-6 py-3 text-center font-mono text-[9px] text-muted">
                Showing the first 80 matching files
              </div>
            ) : null}
          </div>
        </div>
      ) : (
        <ul className="max-h-[560px] overflow-auto p-5 font-mono sm:px-7">
          {tree.map((node) => (
            <TreeNode key={node.path} node={node} />
          ))}
        </ul>
      )}
    </section>
  );
}
