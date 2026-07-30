from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class RepoAnalyzeRequest(BaseModel):
    repo_url: str = Field(min_length=19, max_length=500)
    branch: str | None = Field(default=None, max_length=255)
    commit: str | None = Field(default=None, min_length=7, max_length=40, pattern=r"^[0-9a-fA-F]+$")
    gemini_api_key: SecretStr = Field(min_length=10, max_length=512)
    model: str | None = Field(default=None, max_length=100)
    provider: str = Field(default="gemini", pattern=r"^(gemini|openai|anthropic)$")

    model_config = ConfigDict(str_strip_whitespace=True)


class RepoProjectResponse(BaseModel):
    id: int
    repo_url: str
    repo_name: str
    branch: str | None
    commit: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepoFileResponse(BaseModel):
    id: int
    path: str
    language: str | None
    file_type: str | None
    size_bytes: int
    importance_score: float

    model_config = ConfigDict(from_attributes=True)


class RepoAnalysisResponse(BaseModel):
    project_id: int
    overview: str
    tech_stack_json: dict[str, Any]
    architecture_summary: str
    folder_summary_json: dict[str, Any]
    important_files_json: list[dict[str, Any]]
    request_flow: str
    data_flow: str
    setup_instructions: str
    reading_order_json: list[dict[str, Any] | str]
    risks: str
    generated_report_markdown: str

    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponse(BaseModel):
    project_id: int
    status: str
    report: RepoAnalysisResponse
