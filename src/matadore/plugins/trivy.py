"""Trivy plugin - container image and filesystem vulnerability scanning."""

from __future__ import annotations

from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class Trivy(BasePlugin):
    """Wrapper around `aquasecurity/trivy` for image and dependency scanning.

    Supported target types: ``docker_registry``, ``repo``.
    """

    name = "trivy"
    supported_types = {"docker_registry", "repo"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        if ctx.dry_run:
            return PluginResult(
                plugin=self.name,
                target=target,
                skipped=True,
                skip_reason="dry_run=True - trivy will scan image: " + target,
            )
        raise NotImplementedError
