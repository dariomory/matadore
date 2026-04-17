"""GitLeaks plugin - secret and credential scanning in git history."""

from __future__ import annotations

from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class GitLeaks(BasePlugin):
    """Wrapper around `gitleaks` for secret detection in repositories.

    Supported target types: ``repo``, ``github_org``.
    """

    name = "gitleaks"
    supported_types = {"repo", "github_org"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        if ctx.dry_run:
            return PluginResult(
                plugin=self.name,
                target=target,
                skipped=True,
                skip_reason="dry_run=True - gitleaks will clone (read-only): " + target,
            )
        raise NotImplementedError
