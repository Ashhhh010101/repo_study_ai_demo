# Security Policy

## Supported versions

Security fixes are applied to the latest release on the default branch.

| Version | Supported |
| --- | --- |
| `0.2.x` / `main` | Yes |
| `< 0.2` | No |

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability.

Use [GitHub's private vulnerability reporting flow](https://github.com/Ashhhh010101/repo_study_ai_demo/security/advisories/new). Include:

- The affected component and commit/version.
- Reproduction steps or a minimal proof of concept.
- Expected impact and any known mitigations.
- Whether a provider key, local file, or repository content may have been exposed.

Please allow maintainers a reasonable period to investigate and coordinate a fix before public disclosure. You should receive an initial acknowledgement within seven days.

## Security model

Repo Study AI is designed as a local-first, single-user development tool. The trusted boundary is the machine and OS account running the backend.

### Data that remains local

- Gemini provider key after the active request completes.
- Shallow-cloned public repositories.
- SQLite metadata, code chunks, reports, and chat history.
- The lexical retrieval index.

The key is never intentionally persisted. Repository-derived data and chat are persisted locally.

### Data sent to Gemini

- Selected contents from high-priority repository files.
- Folder/file summaries and bounded report context.
- A question, recent local chat context, and retrieved code chunks during Q&A.

Common credential file names and credential-shaped values are filtered/redacted first. Automated redaction cannot recognize every secret format.

### Implemented controls

- GitHub HTTPS URL allowlist; no arbitrary clone hosts or embedded credentials.
- Strict branch validation and shell-free subprocess arguments.
- Shallow, no-tag, non-interactive clones with LFS smudging disabled and a timeout.
- Symlink rejection and root-bounded scanning.
- Per-file, file-count, total-byte, and provider timeout limits.
- Sensitive filename filtering and outbound credential-pattern redaction.
- Pydantic `SecretStr` API fields and validation errors without echoed input.
- Provider authentication in `x-goog-api-key`, never in the URL.
- Sanitized provider and project error messages.
- Configured CORS origins, trusted hosts, no-store API responses, and baseline browser security headers.
- No raw HTML execution in generated Markdown.
- Least-privilege CI plus dependency update/audit automation.

### Out of scope / not yet provided

- User authentication or authorization.
- Multi-tenant isolation.
- Rate limiting, quotas, or abuse prevention.
- Encrypted application storage.
- Sandboxed execution of repository code. The application does not intentionally execute cloned repository code.
- Guaranteed detection of all secrets or prompt-injection content.
- Support for private repositories.

Do not place this service on the public internet until the missing controls appropriate to that deployment are implemented.

## BYOK operator guidance

- Prefer a Gemini authorization key. If using a standard key, restrict it to the Gemini API and set the narrowest feasible quota.
- Use a dedicated key for this tool; do not reuse a broad production credential.
- Serve the frontend and API over HTTPS if traffic ever leaves localhost.
- Configure reverse proxies to avoid request-body/header logging and explicitly redact provider-key headers.
- Never add provider keys to `.env`, frontend build variables, tests, screenshots, issues, or CI secrets for this project.
- Rotate the key immediately if it appears in logs, browser recordings, commits, or issue content.

## Repository administrator checklist

For the public GitHub repository, enable Dependabot alerts/security updates, secret scanning, push protection, and CodeQL/default code scanning in **Settings → Code security and analysis**.
