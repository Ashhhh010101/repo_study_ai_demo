from pathlib import Path
import hashlib
import json
from threading import Lock

from app.core.config import get_settings


class LocalRepoStore:
    _locks: dict[str, Lock] = {}
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_repo_key(self, repo_url: str, branch: str | None, commit: str | None) -> str:
        value = f"{repo_url.lower().rstrip('/')}|{branch or ''}|{commit or ''}"
        return hashlib.sha256(value.encode()).hexdigest()[:32]

    def get_repo_path(self, repo_url: str, branch: str | None, commit: str | None) -> Path:
        return self.settings.repos_dir / self.get_repo_key(repo_url, branch, commit)

    @classmethod
    def lock_for(cls, key: str) -> Lock:
        cls._locks.setdefault(key, Lock())
        return cls._locks[key]

    @staticmethod
    def write_metadata(path: Path, repo_url: str, branch: str | None, commit: str | None) -> None:
        (path / ".repo-study-meta.json").write_text(
            json.dumps({"repo_url": repo_url, "branch": branch, "commit": commit}), encoding="utf-8"
        )
