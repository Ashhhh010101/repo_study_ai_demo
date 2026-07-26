# Contributing

Thanks for helping improve Repo Study AI.

## Before you start

- Search existing issues and pull requests.
- Use an issue for substantial features or architecture changes before implementation.
- Keep changes focused. Separate refactors from behavior changes where practical.
- Never include a real API key, token, private repository, database, generated clone, or chat transcript.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Local setup

Follow the [README quick start](README.md#quick-start). Install development dependencies with:

```bash
cd backend
python -m pip install -r requirements-dev.txt
```

```bash
cd frontend
npm ci
```

## Development expectations

- Preserve the local-first security boundary.
- Treat cloned repositories, user questions, and model output as untrusted.
- Keep provider keys in transient secret types and out of URLs, logs, exceptions, storage, analytics, and browser persistence.
- Add or update tests for behavior changes and security boundaries.
- Keep API contracts typed on both backend and frontend.
- Make UI changes accessible, responsive, keyboard-operable, and respectful of reduced-motion preferences.

## Checks

Run before opening a pull request:

```bash
cd backend
python -m compileall app
pytest
pip-audit -r requirements.txt
```

```bash
cd frontend
npm run build
npm audit --audit-level=high
```

## Pull requests

Include:

- What changed and why.
- Security/privacy impact, especially for BYOK or repository content.
- Verification performed.
- Screenshots for visible UI changes.
- Any follow-up work or known limitations.

The project uses the MIT license. By submitting a contribution, you agree that it may be distributed under that license.
