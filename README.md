# Repo Study AI

[![CI](https://github.com/Ashhhh010101/repo_study_ai_demo/actions/workflows/ci.yml/badge.svg)](https://github.com/Ashhhh010101/repo_study_ai_demo/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-9dfc75.svg)](LICENSE)
[![Security policy](https://img.shields.io/badge/security-policy-6edcff.svg)](SECURITY.md)

Repo Study AI is a local-first workspace for understanding unfamiliar public GitHub repositories. It shallow-clones a repository, ranks and indexes the code, generates an evidence-grounded architecture brief, and answers follow-up questions against retrieved source chunks.

The project uses bring your own key (BYOK) for Gemini. Provider keys are held only in volatile client/backend memory for the lifetime of a request. They are never written to the database, logs, URLs, local storage, or session storage by application code.

> [!IMPORTANT]
> This is a local-first single-user application. Do not expose the backend directly to an untrusted network. A shared deployment requires authentication, authorization, tenant isolation, rate limiting, encrypted storage, and an external job queue.

## What it does

- Detects languages, frameworks, entrypoints, configuration, and important files.
- Builds a structured report covering architecture, request/data flow, setup, reading order, and unknowns.
- Retrieves line-aware code chunks for repository-grounded Q&A.
- Stores cloned public code, the local index, generated reports, and chat history on the machine running the backend.
- Filters common credential files and credential-shaped values before provider requests.
- Rejects non-GitHub URLs, unsafe branch names, symlinks, oversized files, and repositories beyond configured scan limits.

## Architecture

```text
React client
  │  repository URL + ephemeral Gemini key
  ▼
FastAPI boundary
  ├─ validate URL / branch / request size
  ├─ shallow clone public GitHub repository
  ├─ scan, rank, chunk, and build local index
  ├─ redact common secret patterns
  └─ call Gemini with x-goog-api-key header
        │
        ▼
SQLite + local vector store
  (repository metadata, code chunks, reports, chat — never the provider key)
```

See [Architecture](docs/ARCHITECTURE.md) and the [Security model](SECURITY.md) for boundaries and deployment assumptions.

## Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, SQLite, HTTPX
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Analysis: Git shallow clone, bounded file scanner, importance ranking, local lexical retrieval
- AI provider: Gemini REST API with a user-supplied key

## Repository layout

```text
.
├── .github/              CI, dependency updates, issue and PR templates
├── backend/
│   ├── app/
│   │   ├── api/          HTTP routes
│   │   ├── core/         Settings and security helpers
│   │   ├── db/           SQLAlchemy models and sessions
│   │   ├── repo_analyzer Clone, scan, rank, prompt, and report pipeline
│   │   ├── services/     Analysis, retrieval, report, embedding, and LLM services
│   │   └── storage/      Local repository and vector stores
│   └── tests/
├── docs/                 Architecture and maintainer documentation
└── frontend/
    └── src/
        ├── api/          Typed backend client
        ├── components/   UI building blocks
        ├── context/      Volatile BYOK state
        ├── pages/        Analyzer and report workspaces
        └── types/        API contracts
```

## Quick start

Prerequisites:

- Python 3.10+
- Node.js 20.19+ or 22.12+
- Git
- A Gemini authorization key or API-restricted standard key

Google recommends restricting keys to the Gemini API. See [Google's Gemini key guidance](https://ai.google.dev/gemini-api/docs/generate-content/api-key).

### 1. Start the backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1
```

The API and local documentation are available at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

```bash
cd frontend
npm ci
```

Copy `frontend/.env.example` to `frontend/.env`, then:

```bash
npm run dev
```

Open `http://127.0.0.1:5173`.

## Configuration

Backend settings are documented in [`backend/.env.example`](backend/.env.example):

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./repo_study_ai.db` | Local metadata and content database |
| `DATA_DIR` | `./data` | Runtime data root |
| `REPOS_DIR` | `./data/repos` | Shallow repository clones |
| `VECTOR_STORE_DIR` | `./data/vector_store` | Local retrieval index |
| `MAX_FILE_SIZE_BYTES` | `512000` | Per-file scan cap |
| `MAX_SCANNED_FILES` | `5000` | Scannable file cap |
| `MAX_TOTAL_SCAN_BYTES` | `50000000` | Total accepted source bytes |
| `MAX_CHUNK_CHARS` | `4000` | Retrieval chunk size |
| `ANALYSIS_MAX_WORKERS` | `4` | Concurrent provider summaries |
| `REQUEST_TIMEOUT_SECONDS` | `90` | Gemini request timeout |
| `CLONE_TIMEOUT_SECONDS` | `180` | Git clone timeout |
| `MAX_REPO_CLONE_BYTES` | `200000000` | Preflight and post-clone repository size cap |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | In-memory rate-limit window |
| `ANALYZE_RATE_LIMIT` | `3` | Analyses allowed per client and window |
| `CHAT_RATE_LIMIT` | `20` | Chat requests allowed per client and window |
| `VISIT_RATE_LIMIT` | `10` | Visit events allowed per client and window |
| `RATE_LIMIT_MAX_CLIENTS` | `10000` | Maximum in-memory client rate-limit buckets |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |
| `GEMINI_MAX_OUTPUT_TOKENS` | `8192` | Provider response cap |
| `LLM_TEMPERATURE` | `0.1` | Low-variance generation for consistent reports |
| `SUMMARY_CACHE_ENTRIES` | `512` | In-memory validated file-summary cache size |
| `LLM_TEMPERATURE` | `0.1` | Low-variance generation for consistent reports |
| `CORS_ORIGINS` | local Vite origins | JSON list of allowed browser origins |
| `ALLOWED_HOSTS` | local hosts | JSON list of accepted Host headers |

If the frontend is served from another origin, explicitly add it to `CORS_ORIGINS`. Never use a wildcard for an internet-facing deployment.

## Security and BYOK behavior

- The browser retains the key in React memory only. Refreshing or selecting **Clear** removes it.
- The API models use `SecretStr`, validation responses omit inputs, and provider errors are sanitized.
- Gemini authentication uses the `x-goog-api-key` header, so keys do not enter request URLs.
- Common secret values are redacted before outbound prompts. This is defense in depth, not a guarantee that every possible secret format is recognized.
- Repository files and chat history are local data, but selected repository excerpts, report context, and questions are sent to Gemini.
- Markdown is rendered without raw HTML execution.
- Each analysis returns an opaque project token. Report, file, and chat endpoints require it in the `X-Project-Token` header; the frontend keeps it in session storage for the current tab.

Read [SECURITY.md](SECURITY.md) before deploying or extending support to private repositories.

## Development checks

```bash
cd backend
python -m pip install -r requirements-dev.txt
pytest
pip-audit -r requirements.txt
```

```bash
cd frontend
npm ci
npm run build
npm audit --audit-level=high
```

CI runs backend tests, dependency audits, TypeScript validation, and the production frontend build.

## Contributing

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), follow the [Code of Conduct](CODE_OF_CONDUCT.md), and report vulnerabilities through the private process in [SECURITY.md](SECURITY.md).

## License

Distributed under the [MIT License](LICENSE).
