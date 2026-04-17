"""ScoutSuite plugin - multi-cloud security posture assessment."""

from __future__ import annotations

from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class ScoutSuite(BasePlugin):
    """Wrapper around `nccgroup/ScoutSuite` for cloud configuration auditing.

    Supported target types: ``cloud``.
    """

    name = "scoutsuite"
    supported_types = {"cloud"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        if ctx.dry_run:
            return PluginResult(
                plugin=self.name,
                target=target,
                skipped=True,
                skip_reason=("dry_run=True - scoutsuite will call read-only cloud APIs for: " + target),
            )
        raise NotImplementedError
