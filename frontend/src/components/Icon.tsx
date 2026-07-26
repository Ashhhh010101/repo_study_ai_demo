import type { ReactNode, SVGProps } from "react";

export type IconName =
  | "arrow"
  | "back"
  | "branch"
  | "check"
  | "chevron"
  | "eye"
  | "eyeOff"
  | "file"
  | "folder"
  | "github"
  | "key"
  | "lock"
  | "repo"
  | "search"
  | "send"
  | "shield"
  | "spark"
  | "terminal";

const icons: Record<IconName, ReactNode> = {
  arrow: (
    <>
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </>
  ),
  back: (
    <>
      <path d="M19 12H5" />
      <path d="m11 18-6-6 6-6" />
    </>
  ),
  branch: (
    <>
      <circle cx="6" cy="5" r="2" />
      <circle cx="18" cy="6" r="2" />
      <circle cx="6" cy="19" r="2" />
      <path d="M6 7v10M8 7c4 0 4-1 8-1M8 17c4 0 4-7 8-9" />
    </>
  ),
  check: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="m8 12 2.5 2.5L16 9" />
    </>
  ),
  chevron: <path d="m9 18 6-6-6-6" />,
  eye: (
    <>
      <path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z" />
      <circle cx="12" cy="12" r="2.5" />
    </>
  ),
  eyeOff: (
    <>
      <path d="m3 3 18 18" />
      <path d="M10.6 6.2A9 9 0 0 1 12 6c6 0 9.5 6 9.5 6a15 15 0 0 1-2.1 2.8M6.2 6.3C3.8 8 2.5 12 2.5 12s3.5 6 9.5 6a9.5 9.5 0 0 0 3-.5" />
    </>
  ),
  file: (
    <>
      <path d="M6 2.5h8l4 4V21H6z" />
      <path d="M14 2.5v4h4" />
    </>
  ),
  folder: <path d="M3 6.5h7l2 2h9v10.5H3z" />,
  github: (
    <path d="M12 2.5a9.5 9.5 0 0 0-3 18.5c.5.1.7-.2.7-.5v-1.8c-2.8.6-3.4-1.2-3.4-1.2-.5-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 0 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-4.7 0-1 .4-1.9 1-2.6-.1-.3-.4-1.3.1-2.6 0 0 .8-.3 2.7 1a9.3 9.3 0 0 1 4.9 0c1.8-1.3 2.7-1 2.7-1 .5 1.3.2 2.3.1 2.6.7.7 1 1.6 1 2.6 0 3.6-2.4 4.4-4.6 4.7.4.3.7.9.7 1.8v2.7c0 .3.2.6.7.5A9.5 9.5 0 0 0 12 2.5Z" />
  ),
  key: (
    <>
      <circle cx="8.5" cy="15.5" r="3.5" />
      <path d="m11 13 8-8M16 8l2 2M14 10l2 2" />
    </>
  ),
  lock: (
    <>
      <rect x="4.5" y="10" width="15" height="11" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </>
  ),
  repo: (
    <>
      <path d="M4 3h13a2 2 0 0 1 2 2v16H6a2 2 0 0 1-2-2z" />
      <path d="M8 3v18M8 17h11" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-4-4" />
    </>
  ),
  send: (
    <>
      <path d="m3 3 18 9-18 9 3-9z" />
      <path d="M6 12h15" />
    </>
  ),
  shield: (
    <>
      <path d="M12 2.5 20 6v5.5c0 5-3.4 8.3-8 10-4.6-1.7-8-5-8-10V6z" />
      <path d="m8.5 12 2.2 2.2 4.8-5" />
    </>
  ),
  spark: (
    <>
      <path d="m12 2 1.2 4.3L17 8l-3.8 1.7L12 14l-1.2-4.3L7 8l3.8-1.7z" />
      <path d="m5 14 .8 2.2L8 17l-2.2.8L5 20l-.8-2.2L2 17l2.2-.8zM19 14l.6 1.4L21 16l-1.4.6L19 18l-.6-1.4L17 16l1.4-.6z" />
    </>
  ),
  terminal: (
    <>
      <rect x="2.5" y="4" width="19" height="16" rx="2" />
      <path d="m6 9 3 3-3 3M12 15h5" />
    </>
  )
};

type IconProps = SVGProps<SVGSVGElement> & {
  name: IconName;
  size?: number;
};

export default function Icon({ name, size = 18, ...props }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      fill="none"
      height={size}
      viewBox="0 0 24 24"
      width={size}
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="1.7"
      {...props}
    >
      {icons[name]}
    </svg>
  );
}
