from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    gemini_api_key: str = Field(min_length=10)


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
