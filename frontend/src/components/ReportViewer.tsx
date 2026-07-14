import ReactMarkdown from "react-markdown";

type ReportViewerProps = {
  markdown: string;
};

export default function ReportViewer({ markdown }: ReportViewerProps) {
  return (
    <article className="rounded-[2rem] bg-white/90 p-8 shadow-panel">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </article>
  );
}
