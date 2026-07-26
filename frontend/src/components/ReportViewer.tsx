import Icon from "./Icon";
import ReactMarkdown from "react-markdown";

type ReportViewerProps = {
  markdown: string;
};

export default function ReportViewer({ markdown }: ReportViewerProps) {
  return (
    <section className="surface-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-line px-5 py-4 sm:px-7">
        <div className="flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center rounded-lg border border-line bg-canvas text-accent">
            <Icon name="file" size={16} />
          </span>
          <div>
            <h2 className="text-sm font-semibold text-ink">Architecture brief</h2>
            <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-muted">generated · evidence grounded</p>
          </div>
        </div>
        <span className="hidden items-center gap-1.5 rounded-md border border-accent/15 bg-accent/[0.04] px-2 py-1 font-mono text-[9px] uppercase tracking-[0.12em] text-accent sm:flex">
          <Icon name="check" size={11} />
          complete
        </span>
      </div>
      <article className="report-content px-5 py-7 sm:px-8 sm:py-9">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </article>
    </section>
  );
}
