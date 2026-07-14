import type { FileTreeNode, RepoFile } from "../types/api";

type FileTreeProps = {
  files: RepoFile[];
  tree: FileTreeNode[];
};

function TreeNode({ node, depth = 0 }: { node: FileTreeNode; depth?: number }) {
  const padding = `${depth * 0.85}rem`;
  if (node.type === "file") {
    return (
      <li style={{ paddingLeft: padding }} className="text-sm text-slate">
        {node.name}
      </li>
    );
  }

  return (
    <li>
      <div style={{ paddingLeft: padding }} className="font-medium text-ink">
        {node.name}
      </div>
      <ul className="mt-1 space-y-1">
        {node.children?.map((child) => (
          <TreeNode key={child.path} node={child} depth={depth + 1} />
        ))}
      </ul>
    </li>
  );
}

export default function FileTree({ files, tree }: FileTreeProps) {
  return (
    <div className="grid gap-6 rounded-[2rem] bg-white/90 p-6 shadow-panel lg:grid-cols-[0.9fr_1.1fr]">
      <div>
        <h3 className="font-display text-xl text-ink">Important files</h3>
        <ul className="mt-4 space-y-3 text-sm text-slate">
          {files.map((file) => (
            <li key={file.id} className="rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2">
              <div className="flex items-start justify-between gap-3">
                <span className="break-all font-medium text-ink">{file.path}</span>
                <span className="shrink-0 rounded-full bg-amber-100 px-2 py-1 text-xs text-amber-900">
                  {file.importance_score.toFixed(1)}
                </span>
              </div>
              <div className="mt-1 text-xs uppercase tracking-wide text-slate">
                {file.language ?? "Unknown"} · {file.file_type ?? "Other"}
              </div>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <h3 className="font-display text-xl text-ink">File tree</h3>
        <ul className="mt-4 space-y-2 rounded-2xl border border-stone-200 bg-stone-50 p-4">
          {tree.map((node) => (
            <TreeNode key={node.path} node={node} />
          ))}
        </ul>
      </div>
    </div>
  );
}
