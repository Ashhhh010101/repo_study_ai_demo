import json

import httpx
from pydantic import SecretStr

from app.core.config import get_settings
from app.core.security import redact_sensitive_text


class ProviderError(Exception):
    """A provider failure whose message is safe to expose or persist."""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_text(
        self,
        prompt: str,
        gemini_api_key: SecretStr,
        response_mime_type: str = "text/plain",
    ) -> str:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
        )
        raw_api_key = gemini_api_key.get_secret_value().strip()
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": redact_sensitive_text(
                                prompt,
                                extra_values=(raw_api_key,),
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": response_mime_type,
                "maxOutputTokens": self.settings.gemini_max_output_tokens,
            },
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": raw_api_key,
        }
        try:
            with httpx.Client(
                timeout=self.settings.request_timeout_seconds,
                follow_redirects=False,
            ) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code in {401, 403}:
                message = "Gemini rejected the API key or the key lacks API access."
            elif status_code == 429:
                message = "Gemini rate-limited the request. Try again after the quota resets."
            else:
                message = f"Gemini returned an upstream error (HTTP {status_code})."
            raise ProviderError(message) from None
        except httpx.RequestError as exc:
            raise ProviderError("Gemini could not be reached from the backend.") from None

        try:
            data = response.json()
        except ValueError:
            raise ProviderError("Gemini returned an unreadable response.") from None
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as exc:
            response_shape = list(data) if isinstance(data, dict) else type(data).__name__
            raise ProviderError(
                f"Gemini returned an unexpected response shape: {json.dumps(response_shape)}"
            ) from exc
