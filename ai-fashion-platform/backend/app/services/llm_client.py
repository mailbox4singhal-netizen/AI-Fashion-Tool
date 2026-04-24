"""Unified LLM client.

One `complete_json(system, user)` method works with either Anthropic
Claude or OpenAI — provider is chosen via `settings.llm_provider`.
Used by every AI service. Swap providers without touching any
business logic.

If provider == "mock" or no API key is configured, callers should
fall back to their deterministic mock implementations — the services
do this check automatically via `llm_enabled()`.
"""
from __future__ import annotations

import asyncio
import json
import re
from typing import Any, Dict, Optional

from app.config import settings
from app.utils.logger import log_event


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def llm_enabled() -> bool:
    """True iff a real LLM provider is configured with a key."""
    p = (settings.llm_provider or "mock").lower()
    if p == "anthropic":
        return bool(settings.anthropic_api_key.strip())
    if p == "openai":
        return bool(settings.openai_api_key.strip())
    return False


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _extract_json(text: str) -> Dict[str, Any]:
    """Strip markdown fences / preamble and parse JSON.
    LLMs sometimes wrap JSON in ```json fences or add a sentence before it."""
    if not text:
        raise ValueError("Empty LLM response")

    # Try a fenced block first
    m = _JSON_BLOCK_RE.search(text)
    candidate = m.group(1) if m else text

    # Find the outermost {...} if there's prose around it
    first = candidate.find("{")
    last = candidate.rfind("}")
    if first != -1 and last != -1 and last > first:
        candidate = candidate[first : last + 1]

    return json.loads(candidate.strip())


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

class _AnthropicProvider:
    """Thin wrapper around the official `anthropic` SDK."""

    def __init__(self) -> None:
        from anthropic import AsyncAnthropic  # lazy import

        self._client = AsyncAnthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.llm_timeout_seconds,
        )
        self._model = settings.anthropic_model

    async def complete(self, system: str, user: str) -> str:
        msg = await self._client.messages.create(
            model=self._model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        # Messages API returns a list of content blocks — concat text ones.
        return "".join(
            block.text for block in msg.content if getattr(block, "type", "") == "text"
        )


class _OpenAIProvider:
    """Thin wrapper around the official `openai` SDK (v1+)."""

    def __init__(self) -> None:
        from openai import AsyncOpenAI  # lazy import

        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.llm_timeout_seconds,
        )
        self._model = settings.openai_model

    async def complete(self, system: str, user: str) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""


# ---------------------------------------------------------------------------
# Public client
# ---------------------------------------------------------------------------

class LLMClient:
    """Singleton-style provider router. Use `get_llm_client()`."""

    def __init__(self) -> None:
        provider = (settings.llm_provider or "mock").lower()
        self.provider_name = provider

        if provider == "anthropic":
            self._provider: Optional[Any] = _AnthropicProvider()
        elif provider == "openai":
            self._provider = _OpenAIProvider()
        else:
            self._provider = None  # mock mode

    async def complete_json(
        self,
        system: str,
        user: str,
        *,
        retries: int = 1,
    ) -> Dict[str, Any]:
        """Prompt the LLM and parse its response as JSON.

        Raises on unrecoverable failure — callers should catch and fall
        back to their mock path if desired.
        """
        if self._provider is None:
            raise RuntimeError("LLM is in mock mode — do not call complete_json.")

        last_err: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                raw = await self._provider.complete(system, user)
                log_event(
                    "llm.response",
                    provider=self.provider_name,
                    attempt=attempt,
                    chars=len(raw),
                )
                return _extract_json(raw)
            except (json.JSONDecodeError, ValueError) as e:
                last_err = e
                log_event(
                    "llm.parse_error",
                    provider=self.provider_name,
                    attempt=attempt,
                    error=str(e),
                )
                # retry once on parse error
                if attempt < retries:
                    await asyncio.sleep(0.3)
                    continue
                raise
            except Exception as e:  # network / auth / rate-limit etc.
                last_err = e
                log_event(
                    "llm.error",
                    provider=self.provider_name,
                    attempt=attempt,
                    error=str(e),
                )
                raise

        # unreachable, but keeps type checkers happy
        raise last_err or RuntimeError("LLM call failed")


_singleton: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _singleton
    if _singleton is None:
        _singleton = LLMClient()
    return _singleton
