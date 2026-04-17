"""Nuclei plugin - template-based vulnerability scanning."""

from __future__ import annotations

from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class Nuclei(BasePlugin):
    """Wrapper around `projectdiscovery/nuclei` for CVE and misconfiguration detection.

    Supported target types: ``domain``, ``network``.
    """

    name = "nuclei"
    supported_types = {"domain", "network"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        if ctx.dry_run:
            return PluginResult(
                plugin=self.name,
                target=target,
                skipped=True,
                skip_reason="dry_run=True - nuclei will scan: " + target,
            )
        raise NotImplementedError
