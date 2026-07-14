from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Repo Study AI"
    database_url: str = "sqlite:///./repo_study_ai.db"
    data_dir: Path = Field(default=Path("./data"))
    repos_dir: Path = Field(default=Path("./data/repos"))
    vector_store_dir: Path = Field(default=Path("./data/vector_store"))
    max_file_size_bytes: int = 512_000
    max_chunk_chars: int = 4_000
    request_timeout_seconds: int = 90
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.repos_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    return settings
