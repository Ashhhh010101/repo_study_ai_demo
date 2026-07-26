import { FormEvent, useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import type { ChatResponse } from "../types/api";
import ErrorBox from "./ErrorBox";
import Icon from "./Icon";

type ChatEntry = {
  role: "user" | "assistant";
  content: string;
  used_chunks?: ChatResponse["used_chunks"];
};

type ChatPanelProps = {
  geminiApiKey: string;
  onAsk: (message: string) => Promise<ChatResponse>;
};

const starterQuestions = [
  "Where does request handling begin?",
  "Explain the main data flow.",
  "What should I read first?"
];

export default function ChatPanel({ geminiApiKey, onAsk }: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const historyEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [history, loading]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim() || !geminiApiKey.trim() || loading) {
      return;
    }

    const currentMessage = message.trim();
    setHistory((current) => [...current, { role: "user", content: currentMessage }]);
    setMessage("");
    setError(null);
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
    } catch (err) {
      setError(err instanceof Error ? err.message : "The repository assistant could not answer.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="surface-card flex min-h-[660px] flex-col overflow-hidden xl:max-h-[calc(100vh-7rem)]">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center rounded-lg border border-cyan/20 bg-cyan/[0.05] text-cyan">
            <Icon name="spark" size={16} />
          </span>
          <div>
            <h2 className="text-sm font-semibold text-ink">Repository copilot</h2>
            <p className="font-mono text-[9px] uppercase tracking-[0.13em] text-muted">retrieval grounded</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 font-mono text-[8px] uppercase tracking-[0.12em] text-muted">
          <span className={`h-1.5 w-1.5 rounded-full ${geminiApiKey ? "bg-accent" : "bg-danger"}`} />
          {geminiApiKey ? "key ready" : "key required"}
        </div>
      </div>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4" aria-live="polite">
        {!history.length ? (
          <div className="flex h-full min-h-[330px] flex-col items-center justify-center px-3 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-xl border border-line bg-canvas text-muted">
              <Icon name="terminal" size={21} />
            </div>
            <h3 className="mt-5 text-sm font-semibold text-ink">Interrogate the architecture</h3>
            <p className="mt-2 max-w-xs text-xs leading-5 text-muted">
              Answers combine the generated report with relevant line-aware code chunks.
            </p>
            <div className="mt-5 flex w-full max-w-sm flex-col gap-2">
              {starterQuestions.map((question) => (
                <button
                  key={question}
                  type="button"
                  onClick={() => setMessage(question)}
                  className="flex items-center justify-between rounded-lg border border-line bg-canvas/60 px-3 py-2.5 text-left text-[11px] text-ink-soft transition hover:border-muted/50 hover:bg-panel-soft"
                >
                  {question}
                  <Icon name="chevron" size={13} className="shrink-0 text-muted" />
                </button>
              ))}
            </div>
          </div>
        ) : null}

        {history.map((entry, index) => (
          <div
            key={`${entry.role}-${index}`}
            className={
              entry.role === "user"
                ? "ml-8 rounded-xl rounded-br-sm bg-accent px-4 py-3 text-[#081007]"
                : "mr-3 rounded-xl rounded-bl-sm border border-line bg-canvas/65 px-4 py-3 text-ink-soft"
            }
          >
            {entry.role === "assistant" ? (
              <div className="chat-markdown text-xs leading-6">
                <ReactMarkdown>{entry.content}</ReactMarkdown>
              </div>
            ) : (
              <p className="whitespace-pre-wrap text-xs font-medium leading-5">{entry.content}</p>
            )}
            {entry.role === "assistant" && entry.used_chunks?.length ? (
              <details className="mt-3 border-t border-line pt-3">
                <summary className="cursor-pointer font-mono text-[8px] uppercase tracking-[0.13em] text-muted">
                  {entry.used_chunks.length} retrieved references
                </summary>
                <div className="mt-2 space-y-1.5">
                  {entry.used_chunks.slice(0, 6).map((chunk, chunkIndex) => (
                    <div key={chunkIndex} className="truncate font-mono text-[9px] text-cyan/75">
                      {(chunk.file_path as string) || "Unknown file"}
                      {chunk.start_line && chunk.end_line
                        ? `:${String(chunk.start_line)}–${String(chunk.end_line)}`
                        : ""}
                    </div>
                  ))}
                </div>
              </details>
            ) : null}
          </div>
        ))}
        {loading ? (
          <div className="mr-16 flex items-center gap-2 rounded-xl border border-line bg-canvas/65 px-4 py-3">
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent [animation-delay:-0.3s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent [animation-delay:-0.15s]" />
            <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-accent" />
          </div>
        ) : null}
        {error ? <ErrorBox message={error} /> : null}
        <div ref={historyEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-line bg-canvas/45 p-4">
        <div className="relative">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={geminiApiKey ? "Ask about this repository…" : "Add your Gemini key above to ask questions"}
            className="min-h-24 w-full resize-none rounded-lg border border-line bg-canvas px-3 pb-11 pt-3 text-xs leading-5 text-ink outline-none transition placeholder:text-muted/50 focus:border-accent/45 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!geminiApiKey || loading}
            maxLength={4000}
          />
          <div className="absolute bottom-2 left-3 font-mono text-[8px] text-muted">
            {message.length.toLocaleString()} / 4,000
          </div>
          <button
            type="submit"
            disabled={loading || !geminiApiKey.trim() || !message.trim()}
            className="absolute bottom-2 right-2 grid h-8 w-8 place-items-center rounded-md bg-accent text-[#071006] transition hover:bg-accent-bright disabled:cursor-not-allowed disabled:bg-line disabled:text-muted"
            aria-label="Ask repository question"
          >
            <Icon name="send" size={15} />
          </button>
        </div>
        <p className="mt-2 text-center font-mono text-[8px] uppercase tracking-[0.1em] text-muted">
          Questions and answers are stored in your local app database
        </p>
      </form>
    </section>
  );
}
