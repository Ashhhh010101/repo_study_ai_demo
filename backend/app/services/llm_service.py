import json
import logging

import httpx
from pydantic import SecretStr

from app.core.config import get_settings
from app.core.security import redact_sensitive_text


class ProviderError(Exception):
    """A provider failure whose message is safe to expose or persist."""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

    def generate_text(
        self,
        prompt: str,
        gemini_api_key: SecretStr,
        response_mime_type: str = "text/plain",
        model: str | None = None,
        provider: str = "gemini",
    ) -> str:
        defaults = {
            "gemini": self.settings.gemini_model,
            "openai": "gpt-5.2",
            "anthropic": "claude-sonnet-4-20250514",
        }
        if provider not in defaults:
            raise ProviderError("The selected AI provider is not supported.")
        selected_model = model or defaults[provider]
        if not selected_model or len(selected_model) > 150:
            raise ProviderError("The selected AI model ID is invalid.")
        endpoints = {"gemini": f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent", "openai": "https://api.openai.com/v1/chat/completions", "anthropic": "https://api.anthropic.com/v1/messages"}
        endpoint = endpoints[provider]
        self.logger.info("LLM request provider=%s model=%s prompt_chars=%s", provider, selected_model, len(prompt))
        raw_api_key = gemini_api_key.get_secret_value().strip()
        if provider == "gemini":
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
        elif provider == "openai":
            payload = {"model": selected_model, "messages": [{"role": "user", "content": redact_sensitive_text(prompt, extra_values=(raw_api_key,))}], "max_tokens": self.settings.gemini_max_output_tokens}
        else:
            payload = {"model": selected_model, "max_tokens": self.settings.gemini_max_output_tokens, "messages": [{"role": "user", "content": redact_sensitive_text(prompt, extra_values=(raw_api_key,))}]}
        headers = {"Content-Type": "application/json"}
        if provider == "gemini": headers["x-goog-api-key"] = raw_api_key
        elif provider == "openai": headers["Authorization"] = f"Bearer {raw_api_key}"
        else: headers.update({"x-api-key": raw_api_key, "anthropic-version": "2023-06-01"})
        try:
            with httpx.Client(
                timeout=self.settings.request_timeout_seconds,
                follow_redirects=False,
            ) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                self.logger.info("LLM response provider=%s model=%s status=%s", provider, selected_model, response.status_code)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code in {401, 403}:
                message = f"{provider.title()} rejected the API key or the key lacks API access."
            elif status_code == 429:
                message = f"{provider.title()} rate-limited the request. Try again after the quota resets."
            else:
                message = f"{provider.title()} returned an upstream error (HTTP {status_code})."
            self.logger.warning("LLM rejected request provider=%s model=%s status=%s", provider, selected_model, status_code)
            raise ProviderError(message) from None
        except httpx.RequestError as exc:
            self.logger.warning("LLM connection failed provider=%s model=%s", provider, selected_model)
            raise ProviderError(f"{provider.title()} could not be reached from the backend.") from None

        try:
            data = response.json()
        except ValueError:
            raise ProviderError(f"{provider.title()} returned an unreadable response.") from None
        try:
            if provider == "gemini": return data["candidates"][0]["content"]["parts"][0]["text"]
            return data["choices"][0]["message"]["content"] if provider == "openai" else data["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            response_shape = list(data) if isinstance(data, dict) else type(data).__name__
            raise ProviderError(
                f"{provider.title()} returned an unexpected response shape: {json.dumps(response_shape)}"
            ) from exc
