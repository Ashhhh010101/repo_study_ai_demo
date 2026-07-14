from pathlib import Path

from app.core.config import get_settings


class LocalRepoStore:
    def __init__(self) -> None:
        self.settings = get_settings()

    def get_project_repo_path(self, project_id: int) -> Path:
        return self.settings.repos_dir / str(project_id)
