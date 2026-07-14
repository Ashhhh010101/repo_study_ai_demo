# Repo Study AI Demo

Repo Study AI is a localhost-first app for understanding public GitHub repositories. It clones a repo, scans and indexes the codebase, generates a structured onboarding report, and answers repo-specific questions using the stored report plus retrieved code chunks.

## Features

- Analyze public GitHub repositories from a URL and optional branch.
- Generate a repo onboarding report with stack, structure, key files, and next-reading guidance.
- Ask follow-up questions grounded in the generated report and retrieved file chunks.
- Keep LLM provider keys out of storage by passing the Gemini key per request.
- Run locally with SQLite by default.

## Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, SQLite
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Repo analysis: local git clone, file scanning, importance ranking, chunking, local retrieval
- LLM: Gemini bring-your-own-key through direct Gemini REST API

## Repository Layout

```text
backend/   FastAPI app, database models, repo analysis, retrieval, LLM services
frontend/  React/Vite UI
```

## Prerequisites

- Python 3.10 or newer
- Node.js 20 or newer
- Git
- Gemini API key

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Frontend Setup

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:5173`.

On macOS or Linux, copy env files with:

```bash
cp .env.example .env
```

## Environment Variables

Backend variables are listed in [backend/.env.example](backend/.env.example).

```env
DATABASE_URL=sqlite:///./repo_study_ai.db
DATA_DIR=./data
REPOS_DIR=./data/repos
VECTOR_STORE_DIR=./data/vector_store
MAX_FILE_SIZE_BYTES=512000
MAX_CHUNK_CHARS=4000
REQUEST_TIMEOUT_SECONDS=90
GEMINI_MODEL=gemini-2.5-flash
```

Frontend variables are listed in [frontend/.env.example](frontend/.env.example).

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Do not commit real `.env` files. User-provided Gemini API keys are sent with analysis/chat requests and are not stored in the database.

## API Overview

- `POST /api/repos/analyze`
- `GET /api/repos/{project_id}`
- `GET /api/repos/{project_id}/report`
- `GET /api/repos/{project_id}/files`
- `POST /api/chat/{project_id}`

## Local Checks

Backend syntax check:

```bash
cd backend
python -m compileall app
```

Frontend production build:

```bash
cd frontend
npm run build
```

The GitHub Actions workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml) runs these checks on pushes and pull requests.

## Deployment Notes

- Deploy the frontend to a static host such as Vercel, Netlify, or Cloudflare Pages.
- Deploy the backend to a Python host such as Render, Railway, Fly.io, or a VPS.
- Set `VITE_API_BASE_URL` to the deployed backend URL in the frontend host.
- SQLite is fine for local demos. For production or shared usage, use a managed database and update `DATABASE_URL`.
- Persist or externalize `DATA_DIR` if cloned repos and vector-store data should survive restarts.

## Security Notes

- Real env files, local databases, virtual environments, dependency folders, caches, and generated data are ignored by Git.
- Keep provider API keys on the backend/request boundary only. Do not expose private server-side keys in frontend env variables.
- The app clones public repositories locally, so deploy it with sensible disk limits and request timeouts.

## License

MIT. See [LICENSE](LICENSE).
