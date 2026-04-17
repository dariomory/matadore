"""Nmap plugin - network port and service fingerprinting."""

from __future__ import annotations

from matadore.models.finding import RawFinding
from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class Nmap(BasePlugin):
    """Wrapper around ``nmap`` for port scanning and service detection.

    Supported target types: ``domain``, ``network``.
    """

    name = "nmap"
    supported_types = {"domain", "network"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        if ctx.dry_run:
            return PluginResult(
                plugin=self.name,
                target=target,
                skipped=True,
                skip_reason="dry_run=True - nmap will probe: " + target,
            )
        raise NotImplementedError
