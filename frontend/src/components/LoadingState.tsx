type LoadingStateProps = {
  title: string;
  detail?: string;
};

export default function LoadingState({ title, detail }: LoadingStateProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-accent/20 bg-panel p-5 shadow-panel">
      <div className="flex items-start gap-4">
        <div className="relative mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-accent/20 bg-accent/[0.06]">
          <span className="h-3 w-3 animate-spin rounded-full border-2 border-accent/20 border-t-accent" />
        </div>
        <div>
          <p className="text-sm font-semibold text-ink">{title}</p>
          {detail ? <p className="mt-1.5 text-xs leading-5 text-muted">{detail}</p> : null}
        </div>
      </div>
      <div className="mt-4 h-0.5 overflow-hidden rounded-full bg-line">
        <div className="h-full w-1/3 animate-[scan_1.8s_ease-in-out_infinite] rounded-full bg-accent shadow-glow" />
      </div>
    </div>
  );
}
