import { AppLink } from "../context/RouterContext";
import Icon from "./Icon";

const sourceUrl =
  import.meta.env.VITE_SOURCE_URL ?? "https://github.com/Ashhhh010101/repo_study_ai_demo";

export default function AppHeader() {
  return (
    <header className="relative z-20 border-b border-line/80 bg-canvas/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1440px] items-center justify-between px-5 sm:px-8">
        <AppLink to="/" className="group flex items-center gap-3" aria-label="Repo Study AI home">
          <span className="grid h-9 w-9 place-items-center rounded-lg border border-accent/30 bg-accent/10 text-accent shadow-glow">
            <Icon name="repo" size={19} />
          </span>
          <span>
            <span className="block text-sm font-semibold tracking-tight text-ink">
              Repo Study <span className="text-accent">AI</span>
            </span>
            <span className="block font-mono text-[9px] uppercase tracking-[0.2em] text-muted">
              codebase intelligence
            </span>
          </span>
        </AppLink>

        <div className="flex items-center gap-3 sm:gap-5">
          <div className="hidden items-center gap-2 font-mono text-[10px] uppercase tracking-[0.14em] text-muted sm:flex">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-40" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
            </span>
            local engine
          </div>
          <a
            href={sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex h-9 items-center gap-2 rounded-lg border border-line bg-panel px-3 text-xs font-medium text-ink transition hover:border-muted/50 hover:bg-panel-soft"
          >
            <Icon name="github" size={16} />
            <span className="hidden sm:inline">Source</span>
          </a>
        </div>
      </div>
    </header>
  );
}
