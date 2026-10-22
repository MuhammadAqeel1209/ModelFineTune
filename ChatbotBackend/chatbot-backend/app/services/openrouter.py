import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.core.config import Settings
from app.schemas.chat import ChatMessage


class OpenRouterError(Exception):
    """Safe, user-facing category for provider failures."""


class OpenRouterService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client and self.client is not None:
            await self.client.aclose()

    def _payload_messages(self, messages: list[Any]) -> list[dict[str, Any]]:
        return [message.model_dump() if isinstance(message, ChatMessage) else message for message in messages]

    async def create_completion(self, messages: list[Any]) -> str:
        client = self.client or httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0))
        if self.client is None:
            self.client = client

        url = f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.openrouter_model,
            "messages": self._payload_messages(messages),
        }
        try:
            response = await client.post(
                url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "OpenRouter Chatbot",
                },
            )
            response.raise_for_status()
            data: Any = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not isinstance(content, str) or not content.strip():
                raise OpenRouterError("The AI provider returned an invalid response")
            return content.strip()
        except httpx.TimeoutException as exc:
            raise OpenRouterError("The AI provider timed out. Please try again.") from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            provider_code = ""
            try:
                error_data = exc.response.json().get("error", {})
                provider_code = str(error_data.get("code", ""))
            except (ValueError, TypeError, AttributeError):
                pass

            if status_code in (401, 403):
                message = "OpenRouter rejected the API key. Check OPENROUTER_API_KEY."
            elif status_code == 402:
                message = "OpenRouter requires available credits for this model."
            elif status_code == 404:
                message = "The configured OpenRouter model was not found. Check OPENROUTER_MODEL."
            elif status_code == 429:
                message = "OpenRouter rate limit reached. Please wait and try again."
            elif status_code >= 500:
                message = "OpenRouter is temporarily unavailable. Please try again."
            else:
                message = "OpenRouter rejected the request. Check the model and request settings."

            if provider_code:
                message = f"{message} (provider code: {provider_code})"
            raise OpenRouterError(message) from exc
        except (httpx.HTTPError, ValueError, TypeError, IndexError, KeyError) as exc:
            raise OpenRouterError("The AI provider is temporarily unavailable.") from exc

    async def stream_completion(self, messages: list[Any]) -> AsyncIterator[str]:
        client = self.client or httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=10.0))
        if self.client is None:
            self.client = client

        url = f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.openrouter_model,
            "messages": self._payload_messages(messages),
            "stream": True,
        }
        try:
            async with client.stream(
                "POST", url, json=payload,
                headers={
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "OpenRouter Chatbot",
                },
            ) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    request_response = httpx.Response(response.status_code, request=response.request, content=body)
                    request_response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                    except (ValueError, TypeError, IndexError, KeyError):
                        continue
                    if isinstance(delta, str) and delta:
                        yield delta
        except httpx.TimeoutException as exc:
            raise OpenRouterError("The AI provider timed out. Please try again.") from exc
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code in (401, 403):
                message = "OpenRouter rejected the API key. Check OPENROUTER_API_KEY."
            elif status_code == 402:
                message = "OpenRouter requires available credits for this model."
            elif status_code == 404:
                message = "The configured OpenRouter model was not found. Check OPENROUTER_MODEL."
            elif status_code == 429:
                message = "OpenRouter rate limit reached. Please wait and try again."
            else:
                message = "OpenRouter rejected the streaming request. Check the model and request settings."
            raise OpenRouterError(message) from exc
        except httpx.HTTPError as exc:
            raise OpenRouterError("The AI provider connection was interrupted.") from exc

