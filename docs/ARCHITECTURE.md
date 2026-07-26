# Architecture

## Goals

Repo Study AI converts an unfamiliar public repository into a bounded, evidence-backed onboarding workspace while keeping provider-key custody with the user.

The core design constraints are:

- Local-first persistence.
- Public GitHub repositories only.
- No execution of cloned code.
- Ephemeral provider credentials.
- Explicit resource bounds around untrusted repositories.
- Graceful local fallbacks when the model cannot produce a valid result.

## Components

### React frontend

The frontend owns the interactive workflow and typed API client. The Gemini key is stored in a React context only. It is not placed in navigation state, URLs, browser storage, or build-time environment variables.

The frontend sends the key only in analysis and chat request bodies. Network requests use `no-store`, omit credentials, and suppress referrer information.

### FastAPI boundary

Routes validate bounded request models. BYOK fields use Pydantic `SecretStr`. A custom validation handler excludes raw input values, and API responses receive no-store and baseline security headers.

CORS origins and accepted Host headers are explicit settings with localhost defaults.

### Repository analysis pipeline

1. Validate and canonicalize the GitHub URL and optional branch.
2. Create a project record with a state-machine-style status.
3. Perform a shallow, non-interactive clone with a timeout.
4. Scan regular files only while enforcing file and byte limits.
5. Detect the stack and rank files by structural importance.
6. Persist file metadata and line-aware chunks.
7. Build the local lexical retrieval index.
8. Summarize high-priority files/folders and generate the architecture report.

### Provider boundary

Before an outbound call, common credential formats and the active provider key are removed from the prompt. The key is passed in the Gemini `x-goog-api-key` header. Redirects are disabled, responses are bounded by a timeout, and errors are translated to sanitized messages.

Repository content is delimited as untrusted data in prompts. This reduces prompt-injection risk but cannot eliminate it.

### Persistence

SQLite stores project metadata, file/chunk content, reports, and chat history. The local vector store persists lexical token counts and chunk payloads. Shallow repository clones live under the configured data root.

Provider keys are not represented in database models.

## Trust boundaries

| Boundary | Trusted | Untrusted |
| --- | --- | --- |
| Browser → API | Application code | Request fields and key syntax |
| API → Git | Fixed Git executable/config | Repository URL, branch, remote content |
| Scanner → local OS | Configured repository root | Files, names, sizes, symlinks |
| API → Gemini | Fixed HTTPS endpoint | Repository content, user question, model output |
| Model → UI | Markdown renderer defaults | Generated Markdown and retrieved citations |

## Analysis states

```text
pending → cloning → scanning → indexing → analyzing → completed
    └────────────── any pipeline error ──────────────→ failed
```

## Extension points

- Replace the lexical vector store behind `EmbeddingService`/`RetrievalService`.
- Add providers behind `LLMService` while preserving the ephemeral-secret contract.
- Move analysis to a job queue before supporting concurrent/shared deployments.
- Add database migrations before evolving persisted models in production.
- Introduce an authorization layer before private-repository support.
