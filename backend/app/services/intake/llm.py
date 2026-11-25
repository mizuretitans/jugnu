"""Connection to the AI model. The rest of the app only sees the LLM interface."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from openai import OpenAI

from app.config import Settings, get_settings
from app.errors import ApiError

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
TIMEOUT_SECONDS = 25.0  # one chat turn makes up to three calls


class LLM:
    """Anything with these two methods works (see OpenRouterLLM and ScriptedLLM)."""

    def reply(self, system: str, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    def extract_json(self, system: str, user_text: str) -> dict[str, Any]:
        raise NotImplementedError


def parse_json_object(text: str) -> dict[str, Any]:
    """Pull the first JSON object out of a model reply (tolerates ``` fences)."""
    if not text:
        return {}
    cleaned = re.sub(r"```(?:json)?", "", text).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        return {}
    try:
        data = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _text_of(response: Any) -> str:
    if not response.choices:
        return ""
    content = response.choices[0].message.content
    return content.strip() if isinstance(content, str) else ""


class OpenRouterLLM(LLM):
    """OpenRouter through its OpenAI-compatible API."""

    def __init__(self, api_key: str, chat_model: str, extract_model: str) -> None:
        self._client = OpenAI(
            base_url=OPENROUTER_BASE_URL, api_key=api_key, timeout=TIMEOUT_SECONDS, max_retries=0
        )
        self._chat_model, self._extract_model = chat_model, extract_model

    def reply(self, system: str, messages: list[dict[str, str]]) -> str:
        response = self._client.chat.completions.create(
            model=self._chat_model,
            max_tokens=1000,
            messages=[{"role": "system", "content": system}, *messages],
        )
        return _text_of(response)

    def extract_json(self, system: str, user_text: str) -> dict[str, Any]:
        response = self._client.chat.completions.create(
            model=self._extract_model,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_text},
            ],
        )
        return parse_json_object(_text_of(response))


@lru_cache(maxsize=1)
def _openrouter(api_key: str, chat_model: str, extract_model: str) -> OpenRouterLLM:
    return OpenRouterLLM(api_key, chat_model, extract_model)


def get_llm(settings: Annotated[Settings, Depends(get_settings)]) -> LLM:
    """FastAPI dependency. Runs before anything is stored, so a missing key stores nothing."""
    if settings.ai_mode == "demo":
        from app.services.intake.scripted import ScriptedLLM

        return ScriptedLLM()
    api_key = settings.openrouter_api_key.get_secret_value()
    if not api_key:
        raise ApiError(503, "ai_unavailable", "The AI guide is not set up on this server yet.")
    return _openrouter(api_key, settings.intake_chat_model, settings.intake_extract_model)


LlmDep = Annotated[LLM, Depends(get_llm)]
