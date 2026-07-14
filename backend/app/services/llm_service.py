import json

import httpx

from app.core.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_text(
        self,
        prompt: str,
        gemini_api_key: str,
        response_mime_type: str = "text/plain",
    ) -> str:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent?key={gemini_api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": response_mime_type},
        }
        with httpx.Client(timeout=self.settings.request_timeout_seconds) as client:
            response = client.post(endpoint, json=payload)
            response.raise_for_status()
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise ValueError(f"Unexpected Gemini response: {json.dumps(data)[:500]}") from exc
