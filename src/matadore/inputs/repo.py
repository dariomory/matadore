"""Input handler for source code repository targets."""

from __future__ import annotations

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class RepoInput(BaseInput):
    """Resolves a GitHub repository slug into its clone URL and HEAD ref.

    Performs a read-only clone for commit history analysis and secret scanning.

    Target type: ``repo``
    """

    target_type = "repo"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        if target.dry_run:
            return [
                ResolvedAsset(
                    asset=target.value,
                    asset_type="repo",
                    metadata={"dry_run": True, "action": "clone (read-only) @ HEAD"},
                )
            ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        return f"[REPO] Will clone (read-only): {target.value} @ HEAD"
