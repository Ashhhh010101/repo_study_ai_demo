from typing import Literal

from pydantic import BaseModel, Field


class FileSummary(BaseModel):
    purpose: str = Field(min_length=10)
    key_responsibilities: list[str] = Field(default_factory=list, max_length=12)
    important_symbols: list[str] = Field(default_factory=list, max_length=20)
    dependencies: list[str] = Field(default_factory=list, max_length=20)
    notes: str = Field(min_length=3)
    confidence: Literal["high", "medium", "low"]
    evidence: list[str] = Field(default_factory=list, max_length=12)


class FolderSummary(BaseModel):
    folder_purpose: str = Field(min_length=10)
    modules: list[str] = Field(default_factory=list, max_length=20)
    important_files: list[str] = Field(default_factory=list, max_length=12)
    how_it_fits: str = Field(min_length=10)
    confidence: Literal["high", "medium", "low"]
    evidence: list[str] = Field(default_factory=list, max_length=12)
