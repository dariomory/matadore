"""LiteLLM-backed inference client.

Supports every provider LiteLLM supports: OpenAI, Anthropic, Google Gemini,
Mistral, Cohere, Azure OpenAI, AWS Bedrock, Ollama, and more.  Provider
routing is automatic from the *model* string prefix - no branching required.

Environment variables such as ``OPENAI_API_KEY`` and ``ANTHROPIC_API_KEY``
are picked up automatically when *api_key* is ``None``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import litellm


@dataclass
class LLMClient:
    """Thin wrapper around :func:`litellm.completion`.

    Args:
        model: LiteLLM model string, e.g. ``"gpt-4o"``,
            ``"claude-opus-4-5"``, ``"gemini/gemini-2.0-flash"``,
            ``"ollama/llama3"``.
        api_key: API key for the chosen LLM provider.  Falls back to the
            standard environment variable for that provider when ``None``.
        base_url: Optional custom endpoint for Azure OpenAI, self-hosted
            vLLM, or a local Ollama instance.
    """

    model: str
    api_key: str | None = None
    base_url: str | None = None

    def complete(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Send *messages* to the configured model and return the reply text.

        Args:
            messages: OpenAI-style message list, e.g.
                ``[{"role": "user", "content": "..."}]``.
            **kwargs: Extra parameters forwarded to :func:`litellm.completion`
                (``temperature``, ``max_tokens``, etc.).

        Returns:
            The assistant reply as a plain string.
        """
        response = litellm.completion(
            model=self.model,
            messages=messages,
            api_key=self.api_key,
            base_url=self.base_url,
            **kwargs,
        )
        return response.choices[0].message.content or ""
