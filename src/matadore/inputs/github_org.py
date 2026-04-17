"""Input handler for GitHub organisation targets."""

from __future__ import annotations

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class GitHubOrgInput(BaseInput):
    """Enumerates all public repositories in a GitHub organisation.

    Also surfaces exposed secrets in commit history, leaked API keys, and
    misconfigured Actions workflows.

    Target type: ``github_org``
    """

    target_type = "github_org"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        if target.dry_run:
            return [
                ResolvedAsset(
                    asset=target.value,
                    asset_type="github_org",
                    metadata={"dry_run": True, "action": "enumerate public repos"},
                )
            ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        return f"[GITHUB_ORG] Will enumerate public repos, secrets in history, exposed keys for: {target.value}"
