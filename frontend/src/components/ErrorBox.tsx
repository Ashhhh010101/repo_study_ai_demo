import Icon from "./Icon";

type ErrorBoxProps = {
  message: string;
};

export default function ErrorBox({ message }: ErrorBoxProps) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-danger/25 bg-danger/[0.055] px-4 py-3.5 text-xs leading-5 text-[#ffb2ba]"
    >
      <Icon name="shield" size={16} className="mt-0.5 shrink-0 text-danger" />
      <span>{message}</span>
    </div>
  );
}
