"""Base class for all Matadore scanner plugins.

Every plugin - built-in or third-party - must subclass :class:`BasePlugin`
and implement :meth:`BasePlugin.run`.  The engine calls ``run()`` for each
applicable target, then feeds the returned :class:`PluginResult` into the
LLM reasoning layer.

Example::

    from matadore.plugins import BasePlugin
    from matadore.models import RawFinding

    class MyScanner(BasePlugin):
        name = "my-scanner"
        supported_types = {"domain", "network"}

        def run(self, target: str, ctx: PluginContext) -> PluginResult:
            raw_output = subprocess.check_output(["my-tool", target], text=True)
            return PluginResult(
                plugin=self.name,
                target=target,
                findings=[
                    RawFinding(plugin=self.name, asset=target, raw=raw_output)
                ],
            )
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any

from matadore.models.finding import RawFinding


@dataclass
class PluginContext:
    """Runtime context passed to every plugin invocation.

    Attributes:
        mode: Scan mode - ``"passive"``, ``"active"``, or ``"stealth"``.
        dry_run: When ``True`` the plugin must not touch the network.
        extra: Arbitrary extra kwargs forwarded from ``engage()``.
    """

    mode: str = "active"
    dry_run: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginResult:
    """Output from a single plugin run.

    Attributes:
        plugin: Name of the plugin that produced these findings.
        target: The asset that was scanned.
        findings: Raw findings for the LLM reasoning layer to process.
        skipped: ``True`` when the plugin declined to run (e.g. passive mode).
        skip_reason: Human-readable explanation when ``skipped`` is ``True``.
    """

    plugin: str
    target: str
    findings: list[RawFinding] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""


class BasePlugin(abc.ABC):
    """Abstract base for all Matadore scanner plugins.

    Subclass this and implement :meth:`run` to create a custom plugin.

    Class attributes:
        name: Unique plugin identifier used in :class:`~matadore.models.finding.RawFinding`
            and audit logs.  Override in every subclass.
        supported_types: Set of target types this plugin can handle.
            ``None`` means the plugin accepts every type.
    """

    name: str = "base"
    supported_types: set[str] | None = None

    def supports(self, target_type: str) -> bool:
        """Return ``True`` if this plugin can handle *target_type*.

        Args:
            target_type: One of ``"domain"``, ``"network"``, ``"repo"``,
                ``"github_org"``, ``"cloud"``, ``"docker_registry"``.
        """
        if self.supported_types is None:
            return True
        return target_type in self.supported_types

    @abc.abstractmethod
    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        """Execute the plugin against *target* and return raw findings.

        Args:
            target: The asset to scan (domain, IP range, repo path, etc.).
            ctx: Runtime context including scan mode and dry-run flag.

        Returns:
            A :class:`PluginResult` containing zero or more raw findings.
        """

    async def run_async(self, target: str, ctx: PluginContext) -> PluginResult:
        """Async wrapper around :meth:`run`.

        The default implementation delegates to the synchronous ``run()``
        method.  Override for truly async plugins (e.g. aiohttp-based tools).
        """
        return self.run(target, ctx)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
