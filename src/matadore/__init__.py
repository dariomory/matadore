"""Matadore - AI-powered attack surface mapping for red teams.

Matadore uses `LiteLLM <https://github.com/BerriAI/litellm>`_ for model
inference, meaning you can plug in any supported provider - OpenAI, Anthropic,
Google Gemini, Mistral, AWS Bedrock, Ollama, and more - using your own API key.
No data is routed through Matadore's servers.

Quick start::

    from matadore import Matadore

    # OpenAI
    m = Matadore(model="gpt-4o", api_key="sk-...")

    # Anthropic
    m = Matadore(model="claude-opus-4-5", api_key="sk-ant-...")

    # Local model - no data egress
    m = Matadore(model="ollama/llama3")

    report = m.engage("mydomain.com")
    print(report.summary())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from matadore.llm import LLMClient
from matadore.models import Report  # noqa: F401  (re-exported for convenience)

__all__ = ["Matadore"]


@dataclass
class Matadore:
    """AI-powered attack surface mapping for red teams.

    Matadore uses LiteLLM under the hood, so *model* can be any string
    LiteLLM understands - the provider is inferred automatically from the
    prefix (``openai/``, ``anthropic/``, ``gemini/``, ``ollama/``, etc.).

    Args:
        model: LiteLLM model string, e.g. ``"gpt-4o"``,
            ``"claude-opus-4-5"``, ``"gemini/gemini-2.0-flash"``,
            ``"ollama/llama3"``.
        api_key: API key for the chosen LLM provider.  Falls back to the
            standard environment variable for that provider
            (``OPENAI_API_KEY``, ``ANTHROPIC_API_KEY``, etc.) when omitted.
        base_url: Optional custom endpoint - useful for Azure OpenAI,
            self-hosted vLLM, or a local Ollama instance.
        plugins: Additional scanner plugins to load alongside the built-ins.

    Example::

        from matadore import Matadore

        m = Matadore(
            model="gpt-4o",
            api_key="sk-...",
        )
        report = m.engage("mydomain.com")
    """

    model: str
    api_key: str | None = None
    base_url: str | None = None
    plugins: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._llm = LLMClient(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def engage(self, target: str, **kwargs: Any) -> Report:
        """Start an engagement against *target*.

        Args:
            target: Domain, IP range, GitHub org, cloud account, or Docker
                registry to scan.
            **kwargs: Optional parameters:

                - ``type`` - ``"domain"``, ``"network"``, ``"repo"``,
                  ``"github_org"``, ``"cloud"``, ``"docker_registry"``
                - ``mode`` - ``"passive"``, ``"active"`` (default), ``"stealth"``
                - ``dry_run`` - if ``True``, show what would be scanned without
                  touching anything
                - ``stream`` - if ``True``, yield findings as they arrive

        Returns:
            A :class:`~matadore.models.Report` containing the full findings.
        """
        raise NotImplementedError
