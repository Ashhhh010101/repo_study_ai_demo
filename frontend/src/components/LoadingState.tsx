type LoadingStateProps = {
  title: string;
  detail?: string;
};

export default function LoadingState({ title, detail }: LoadingStateProps) {
  return (
    <div className="rounded-3xl border border-amber-200 bg-white/80 p-6 shadow-panel">
      <div className="flex items-center gap-3">
        <div className="h-3 w-3 animate-pulse rounded-full bg-ember" />
        <p className="text-lg font-semibold text-ink">{title}</p>
      </div>
      {detail ? <p className="mt-2 text-sm text-slate">{detail}</p> : null}
    </div>
  );
}
