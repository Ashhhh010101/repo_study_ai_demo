# Repo Study AI Demo

Repo Study AI is a localhost-first MVP for understanding public GitHub repositories. It clones a repo locally, scans and indexes the codebase, generates a structured onboarding report, and then answers repo-specific questions using the stored report plus retrieved chunks.

## Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, SQLite by default with PostgreSQL-ready `DATABASE_URL`
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Repo analysis: local git clone, grounded file scanning, importance ranking, chunking, keyword-backed local retrieval
- LLM: Gemini BYOK via direct Gemini REST API

## 1. Install backend deps

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## 2. Run DB init

The app creates tables automatically on startup. SQLite is the default local DB.

Optional PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/repo_study_ai
```

If you use PostgreSQL, install the driver:

```bash
pip install psycopg[binary]
```

## 3. Start FastAPI

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000`.

## 4. Start frontend

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

## 5. How to use Gemini BYOK

1. Open the frontend.
2. Paste a public GitHub repository URL.
3. Paste your Gemini API key. The key is used per request and is not stored in the database.
4. Optionally specify a branch.
5. Click analyze to generate the report.
6. On the report page, reuse or re-enter the Gemini API key for Q&A.

## API overview

- `POST /api/repos/analyze`
- `GET /api/repos/{project_id}`
- `GET /api/repos/{project_id}/report`
- `GET /api/repos/{project_id}/files`
- `POST /api/chat/{project_id}`

## Notes

- This MVP is synchronous but the service boundaries are set up so analysis can move to background jobs later.
- Retrieval uses a simple local JSON-backed keyword index behind an embedding service abstraction, so you can swap in FAISS or Chroma later without rewriting the app layers.
- The report pipeline is designed to avoid guessing and falls back to grounded structural summaries if the LLM call fails.
