from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

from openai import OpenAI


@dataclass(frozen=True)
class LLMConfig:
    model: str
    temperature: float
    top_p: float


def _get_client() -> OpenAI:
    # OpenAI SDK reads OPENAI_API_KEY from env automatically.
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def chat_completion(
    *,
    system_prompt: str,
    user_message: str,
    history: Iterable[dict] | None = None,
    config: LLMConfig,
) -> str:
    client = _get_client()

    messages: list[dict] = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(list(history))
    messages.append({"role": "user", "content": user_message})

    resp = client.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=float(config.temperature),
        top_p=float(config.top_p),
    )
    return resp.choices[0].message.content or ""
