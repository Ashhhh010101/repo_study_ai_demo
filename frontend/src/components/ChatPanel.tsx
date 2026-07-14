import { FormEvent, useState } from "react";

import type { ChatResponse } from "../types/api";

type ChatEntry = {
  role: "user" | "assistant";
  content: string;
  used_chunks?: ChatResponse["used_chunks"];
};

type ChatPanelProps = {
  geminiApiKey: string;
  onAsk: (message: string) => Promise<ChatResponse>;
};

export default function ChatPanel({ geminiApiKey, onAsk }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || !geminiApiKey.trim()) {
      return;
    }

    const currentMessage = message.trim();
    setHistory((current) => [...current, { role: "user", content: currentMessage }]);
    setMessage("");
    setLoading(true);
    try {
      const response = await onAsk(currentMessage);
      setHistory((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer,
          used_chunks: response.used_chunks
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col rounded-[2rem] bg-white/90 p-6 shadow-panel">
      <div className="mb-4">
        <h3 className="font-display text-xl text-ink">Repo Q&amp;A</h3>
        <p className="mt-1 text-sm text-slate">
          Ask grounded questions like “Where is the API entrypoint?” or “How should I read this repo?”
        </p>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {history.map((entry, index) => (
          <div
            key={`${entry.role}-${index}`}
            className={entry.role === "user" ? "ml-6 rounded-2xl bg-ink px-4 py-3 text-white" : "mr-6 rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3 text-ink"}
          >
            <p className="whitespace-pre-wrap text-sm">{entry.content}</p>
            {entry.role === "assistant" && entry.used_chunks?.length ? (
              <div className="mt-3 border-t border-stone-200 pt-3 text-xs text-slate">
                {entry.used_chunks.slice(0, 4).map((chunk, chunkIndex) => (
                  <div key={chunkIndex}>
                    {(chunk.file_path as string) || "Unknown file"}{" "}
                    {chunk.start_line && chunk.end_line
                      ? `(${String(chunk.start_line)}-${String(chunk.end_line)})`
                      : ""}
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        ))}
        {loading ? <div className="text-sm text-slate">Looking through the indexed repo context...</div> : null}
      </div>
      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask a repo-specific question..."
          className="min-h-28 w-full rounded-2xl border border-stone-300 bg-stone-50 px-4 py-3 text-sm outline-none transition focus:border-ember"
        />
        <button
          type="submit"
          disabled={loading || !geminiApiKey.trim()}
          className="w-full rounded-2xl bg-moss px-4 py-3 text-sm font-semibold text-white transition hover:bg-lime-800 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? "Answering..." : "Ask question"}
        </button>
      </form>
    </div>
  );
}
