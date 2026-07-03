from __future__ import annotations

import json
import re
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


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON from raw LLM output, tolerating markdown code fences."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


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

    def summarize(self, text: str) -> str:
        return self.generate_text(prompt=text).text


class OpenAICompatibleProvider(BaseLLMProvider):
    """OpenAI Chat Completions API — works with OpenAI, OpenClaw, Ollama, OpenRouter."""

    def __init__(
        self,
        *,
        provider_name: str,
        model_name: str,
        api_base: str,
        api_key: str,
        extra_headers: dict[str, str] | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        super().__init__(provider_name=provider_name, model_name=model_name)
        self.api_base = api_base.rstrip("/")
        if not self.api_base.endswith("/chat/completions"):
            self.api_base = f"{self.api_base}/chat/completions"
        self.api_key = api_key
        self.extra_headers = extra_headers or {}
        self.timeout_seconds = timeout_seconds

    def _build_messages(self, prompt: str, system_prompt: str | None) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    @staticmethod
    def _build_usage(payload: dict[str, Any]) -> TokenUsage:
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
        json_mode: bool = False,
    ):
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": self._build_messages(prompt=prompt, system_prompt=system_prompt),
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if json_mode and self.provider_name == "openai":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            **self.extra_headers,
        }
        req = request.Request(
            self.api_base,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            return request.urlopen(req, timeout=self.timeout_seconds)
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="ignore")
            if exc.code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise AIProviderAuthError(response_body) from exc
            if exc.code == HTTPStatus.TOO_MANY_REQUESTS:
                raise AIProviderRateLimitError(response_body) from exc
            raise AIProviderRequestError(response_body) from exc
        except error.URLError as exc:
            raise AIProviderRequestError(
                f"Could not reach {self.provider_name} at {self.api_base}: {exc.reason}"
            ) from exc

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

        text = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
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
            json_mode=True,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))

        text = payload.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        try:
            data = extract_json_object(text)
        except json.JSONDecodeError as exc:
            raise AIProviderRequestError(
                f"{self.provider_name} returned invalid JSON: {text[:200]}"
            ) from exc

        return JSONGenerationResult(
            data=data,
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=self._build_usage(payload),
            raw_response=payload,
        )


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, model_name: str) -> None:
        if not api_key:
            raise AIProviderAuthError("OpenAI API key is required.")
        super().__init__(
            provider_name="openai",
            model_name=model_name,
            api_base="https://api.openai.com/v1/chat/completions",
            api_key=api_key,
        )


class MockLLMProvider(BaseLLMProvider):
    """Deterministic coach responses for local dev when no LLM gateway is configured."""

    _COACH_REPLIES: dict[str, dict[str, Any]] = {
        "reach": {
            "direct_coaching_response": (
                "Your reach dropped 12% this week, but that's normal after a high-performing post — "
                "the algorithm resets expectations. Post a Story poll today to re-engage your warm audience, "
                "then drop a Reel tomorrow at 6am."
            ),
            "recommended_next_actions": [
                "Post a Story poll today",
                "Publish a Reel tomorrow at 6am",
                "Avoid going dark for more than 2 days",
            ],
            "content_ideas": [
                "Behind-the-scenes of your content workflow",
                "What I learned from my last viral post",
                "Audience Q&A in Stories",
            ],
            "risk_warning": None,
        },
        "time": {
            "direct_coaching_response": (
                "Your top engagement windows (last 90 days): Tue 6–8am (7.2% avg), Thu 6pm (6.8%), "
                "Sat 9am (8.5%). Prioritize Saturday morning for your most important content."
            ),
            "recommended_next_actions": [
                "Schedule next Reel for Saturday 9am",
                "Batch-create 3 posts on Tuesday morning",
                "Test Thursday evening for carousel content",
            ],
            "content_ideas": [
                "Weekend morning routine GRWM",
                "Tuesday motivation talking-head",
                "Thursday evening skincare review",
            ],
            "risk_warning": None,
        },
        "hook": {
            "direct_coaching_response": (
                "Your hook rate averages 68% — solid! Top-performing hooks for your audience: "
                "questions that challenge beliefs, unexpected revelations, and identity statements."
            ),
            "recommended_next_actions": [
                "A/B test two hook styles this week",
                "Open next Reel with a contrarian question",
                "Review your top 5 posts and extract hook patterns",
            ],
            "content_ideas": [
                "3 hooks that doubled my saves",
                "Stop scrolling — here's what nobody tells you about...",
                "I was wrong about morning routines",
            ],
            "risk_warning": None,
        },
        "pillar": {
            "direct_coaching_response": (
                "For your niche (lifestyle + beauty, 18–34F), structure around 4 pillars: "
                "Personal story (40%), Education (25%), Aspiration (25%), Community (10%)."
            ),
            "recommended_next_actions": [
                "Map your next 12 posts to the 4 pillars",
                "Increase personal story content this week",
                "Add a community prompt post on Sunday",
            ],
            "content_ideas": [
                "My content pillar breakdown (with examples)",
                "Why I post 40% personal story content",
                "Community spotlight: featuring a follower",
            ],
            "risk_warning": None,
        },
        "default": {
            "direct_coaching_response": (
                "Based on your analytics, focus on consistency over virality. Your audience responds best "
                "to educational content on Thursdays and Saturdays. Engagement rate is 6.3% — 2× industry average."
            ),
            "recommended_next_actions": [
                "Publish 3 posts this week on your best windows",
                "Repurpose your top trend into a carousel",
                "Engage with 20 comments daily for 10 minutes",
            ],
            "content_ideas": [
                "Weekly creator recap",
                "Trending topic + your unique angle",
                "Audience question answered on camera",
            ],
            "risk_warning": None,
        },
    }

    def __init__(self, model_name: str = "mock-coach") -> None:
        super().__init__(provider_name="mock", model_name=model_name)

    @classmethod
    def _coach_payload_for_prompt(cls, prompt: str) -> dict[str, Any]:
        match = re.search(r"User question:\s*(.+?)(?:\n\n|$)", prompt, re.DOTALL | re.IGNORECASE)
        question = (match.group(1) if match else prompt).lower()
        if "drop" in question or "reach" in question:
            key = "reach"
        elif "time" in question or "when" in question:
            key = "time"
        elif "hook" in question:
            key = "hook"
        elif "pillar" in question or "niche" in question:
            key = "pillar"
        else:
            key = "default"
        return dict(cls._COACH_REPLIES[key])

    def generate_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> TextGenerationResult:
        data = self._coach_payload_for_prompt(prompt)
        return TextGenerationResult(
            text=data["direct_coaching_response"],
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=40, total_tokens=50),
        )

    def stream_text(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[StreamTextEvent]:
        text = self.generate_text(prompt, system_prompt=system_prompt).text
        yield StreamTextEvent(
            event="delta",
            text=text,
            provider_name=self.provider_name,
            model_name=self.model_name,
        )
        yield StreamTextEvent(event="done", provider_name=self.provider_name, model_name=self.model_name)

    def generate_json(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> JSONGenerationResult:
        data = self._coach_payload_for_prompt(prompt)
        return JSONGenerationResult(
            data=data,
            provider_name=self.provider_name,
            model_name=self.model_name,
            usage=TokenUsage(prompt_tokens=25, completion_tokens=60, total_tokens=85),
            raw_response={"mock": True},
        )


class _PlaceholderProvider(BaseLLMProvider):
    def __init__(self, provider_name: str, model_name: str) -> None:
        super().__init__(provider_name=provider_name, model_name=model_name)

    def _not_implemented(self) -> AIProviderNotImplementedError:
        return AIProviderNotImplementedError(
            f"{self.provider_name} provider is not configured. "
            f"Set LLM_PROVIDER and credentials in api/.env.local."
        )

    def generate_text(self, prompt: str, **kwargs: Any) -> TextGenerationResult:
        raise self._not_implemented()

    def stream_text(self, prompt: str, **kwargs: Any) -> Iterator[StreamTextEvent]:
        raise self._not_implemented()

    def generate_json(self, prompt: str, **kwargs: Any) -> JSONGenerationResult:
        raise self._not_implemented()


class ClaudeProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="claude", model_name=model_name)


class GeminiProvider(_PlaceholderProvider):
    def __init__(self, model_name: str) -> None:
        super().__init__(provider_name="gemini", model_name=model_name)


def build_provider(
    provider_name: str,
    *,
    api_key: str | None = None,
    model: str = "default",
    api_base: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> BaseLLMProvider:
    normalized = provider_name.strip().lower()

    if normalized == "mock":
        return MockLLMProvider(model_name=model if model != "default" else "mock-coach")
    if normalized == "openai":
        return OpenAIProvider(api_key=api_key or "", model_name=model)
    if normalized == "openclaw":
        if not api_base:
            raise AIProviderRequestError("OPENCLAW_GATEWAY_URL is required for LLM_PROVIDER=openclaw.")
        return OpenAICompatibleProvider(
            provider_name="openclaw",
            model_name=model if model != "default" else "openclaw/default",
            api_base=api_base,
            api_key=api_key or "local",
        )
    if normalized in {"hermes", "hermes-local", "ollama"}:
        if not api_base:
            raise AIProviderRequestError("OLLAMA_BASE_URL is required for LLM_PROVIDER=hermes.")
        return OpenAICompatibleProvider(
            provider_name="hermes-local",
            model_name=model if model != "default" else "hermes3",
            api_base=api_base,
            api_key=api_key or "ollama",
        )
    if normalized == "openrouter":
        if not api_key:
            raise AIProviderAuthError("OPENROUTER_API_KEY is required for LLM_PROVIDER=openrouter.")
        return OpenAICompatibleProvider(
            provider_name="openrouter",
            model_name=model if model != "default" else "nousresearch/hermes-3-llama-3.1-70b",
            api_base=api_base or "https://openrouter.ai/api/v1/chat/completions",
            api_key=api_key,
            extra_headers=extra_headers or {},
        )
    if normalized == "claude":
        return ClaudeProvider(model_name=model)
    if normalized == "gemini":
        return GeminiProvider(model_name=model)

    raise AIProviderRequestError(f"Unsupported LLM provider: {provider_name}")
