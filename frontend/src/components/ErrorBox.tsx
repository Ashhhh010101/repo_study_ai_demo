type ErrorBoxProps = {
  message: string;
};

export default function ErrorBox({ message }: ErrorBoxProps) {
  return (
    <div className="rounded-2xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800 shadow-panel">
      {message}
    </div>
  );
}
