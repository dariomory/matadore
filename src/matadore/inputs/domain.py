"""Input handler for domain and subdomain targets."""

from __future__ import annotations

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class DomainInput(BaseInput):
    """Resolves a domain into its apex record plus discovered subdomains.

    In active mode this performs DNS enumeration and certificate transparency
    log lookups.  In passive mode only publicly available CT log data is used.

    Target type: ``domain``
    """

    target_type = "domain"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        if target.dry_run:
            return [
                ResolvedAsset(
                    asset=target.value,
                    asset_type="domain",
                    metadata={"dry_run": True},
                )
            ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        mode_note = "passive CT log lookup" if target.mode == "passive" else "DNS enumeration + CT logs"
        return f"[DOMAIN] Will resolve and enumerate: {target.value} ({mode_note})"
