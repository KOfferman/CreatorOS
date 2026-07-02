from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Iterator
from urllib import error, request


class AIProviderError(Exception):
    pass


class AIProviderAuthError(AIProviderError):
    pass


class AIProviderRateLimitError(AIProviderError):
    pass


class AIProviderRequestError(AIProviderError):
    pass


class AIProviderNotImplementedError(AIProviderError):
    pass


@dataclass(slots=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(slots=True)
class TextGenerationResult:
    text: str
    provider_name: str
    model_name: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    raw_response: dict[str, Any] | None = None


@dataclass(slots=True)
class JSONGenerationResult:
    data: dict[str, Any]
    provider_name: str
    model_name: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    raw_response: dict[str, Any] | None = None


@dataclass(slots=True)
class StreamTextEvent:
    event: str
    text: str = ""
    usage: TokenUsage | None = None
    provider_name: str = ""
    model_name: str = ""


class BaseLLMProvider(ABC):
    def __init__(self, provider_name: str, model_name: str) -> None:
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> TextGenerationResult:
        raise NotImplementedError

    @abstractmethod
    def stream_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[StreamTextEvent]:
        raise NotImplementedError

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> JSONGenerationResult:
        raise NotImplementedError

    # Backward compatibility for existing caller(s).
    def summarize(self, text: str) -> str:
        return self.generate_text(prompt=text).text


class OpenAIProvider(BaseLLMProvider):
    api_base = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str, model_name: str) -> None:
        if not api_key:
            raise AIProviderAuthError("OpenAI API key is required.")
        super().__init__(provider_name="openai", model_name=model_name)
        self.api_key = api_key

    def _build_messages(self, prompt: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _build_usage(self, payload: dict[str, Any]) -> TokenUsage:
        usage = payload.get("usage", {})
        return TokenUsage(
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
        )

    def _request_completion(
        self,
        *,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int | None,
        stream: bool,
    ):
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": self._build_messages(prompt=prompt, system_prompt=system_prompt),
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        req = request.Request(
            self.api_base,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            return request.urlopen(req, timeout=60)
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="ignore")
            if exc.code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise AIProviderAuthError(response_body) from exc
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise AIProviderRateLimitError(response_body) from exc
            raise AIProviderRequestError(response_body) from exc
        except error.URLError as exc:
            raise AIProviderRequestError(str(exc.reason)) from exc

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> TextGenerationResult:
        with self._request_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        text = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return TextGenerationResult(
            text=text,
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=self._build_usage(payload),
            raw_response=payload,
        )

    def stream_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[StreamTextEvent]:
        with self._request_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        ) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line or not line.startswith("data: "):
                    continue
                payload = line.removeprefix("data: ").strip()
                if payload == "[DONE]":
                    yield StreamTextEvent(
                        event="done",
                        provider_name=self.provider_name,
                        model_name=self.model_name,
                    )
                    continue

                parsed = json.loads(payload)
                delta = parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if delta:
                    yield StreamTextEvent(
                        event="delta",
                        text=delta,
                        provider_name=self.provider_name,
                        model_name=self.model_name,
                    )

    def generate_json(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> JSONGenerationResult:
        with self._request_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        text = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "{}")
        )
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIProviderRequestError("Provider returned invalid JSON.") from exc

        return JSONGenerationResult(
            data=data,
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=self._build_usage(payload),
            raw_response=payload,
        )


class _PlaceholderProvider(BaseLLMProvider):
    def __init__(self, provider_name: str, model_name: str) -> None:
        super().__init__(provider_name=provider_name, model_name=model_name)

    def _not_implemented(self) -> AIProviderNotImplementedError:
        return AIProviderNotImplementedError(
            f"{self.provider_name} provider is a placeholder. "
            f"Implement API integration for model '{self.model_name}'."
        )

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> TextGenerationResult:
        raise self._not_implemented()

    def stream_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[StreamTextEvent]:
        raise self._not_implemented()

    def generate_json(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> JSONGenerationResult:
        raise self._not_implemented()


class ClaudeProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="claude", model_name=model_name)


class GeminiProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="gemini", model_name=model_name)


class OpenRouterProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="openrouter", model_name=model_name)


class HermesLocalProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="hermes-local", model_name=model_name)


def build_provider(
    provider_name: str,
    *,
    api_key: str | None = None,
    model: str = "default",
) -> BaseLLMProvider:
    normalized = provider_name.strip().lower()

    if normalized == "openai":
        return OpenAIProvider(api_key=api_key or "", model_name=model)
    if normalized == "claude":
        return ClaudeProvider(model_name=model)
    if normalized == "gemini":
        return GeminiProvider(model_name=model)
    if normalized == "openrouter":
        return OpenRouterProvider(model_name=model)
    if normalized in {"hermes", "hermes-local"}:
        return HermesLocalProvider(model_name=model)

    raise AIProviderRequestError(f"Unsupported LLM provider: {provider_name}")
