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
    max_file_size_bytes: int = Field(default=512_000, ge=1_024, le=5_000_000)
    max_scanned_files: int = Field(default=5_000, ge=1, le=50_000)
    max_total_scan_bytes: int = Field(
        default=50_000_000,
        ge=10_000,
        le=500_000_000,
    )
    max_chunk_chars: int = Field(default=4_000, ge=500, le=20_000)
    analysis_max_workers: int = Field(default=4, ge=1, le=16)
    request_timeout_seconds: int = Field(default=90, ge=5, le=600)
    clone_timeout_seconds: int = Field(default=180, ge=10, le=1_800)
    rate_limit_window_seconds: int = Field(default=60, ge=10, le=3_600)
    analyze_rate_limit: int = Field(default=3, ge=1, le=100)
    chat_rate_limit: int = Field(default=20, ge=1, le=200)
    gemini_model: str = "gemini-3.5-flash"
    supported_gemini_models: list[str] = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-2.5-pro", "gemini-2.5-flash"]
    gemini_max_output_tokens: int = Field(default=8_192, ge=256, le=65_536)
    cors_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
    allowed_hosts: list[str] = ["127.0.0.1", "localhost", "testserver"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.repos_dir.mkdir(parents=True, exist_ok=True)
    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    return settings
