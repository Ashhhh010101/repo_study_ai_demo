from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4_000)
    gemini_api_key: SecretStr = Field(min_length=10, max_length=512)

    model_config = ConfigDict(str_strip_whitespace=True)


class ChatResponse(BaseModel):
    answer: str
    used_chunks: list[dict[str, Any]]


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    used_chunks_json: list[dict[str, Any]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
