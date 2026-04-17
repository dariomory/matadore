"""Input handler for cloud account/project targets."""

from __future__ import annotations

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset

SUPPORTED_PROVIDERS = {"aws", "gcp", "azure"}


class CloudInput(BaseInput):
    """Audits cloud configuration drift and IAM over-permissioning.

    Uses read-only API calls only (e.g. ``ec2:DescribeInstances``,
    ``s3:ListBuckets``).  Requires the appropriate cloud credentials to be
    available in the environment.

    Target type: ``cloud``

    Extra kwargs:
        provider (str): ``"aws"``, ``"gcp"``, or ``"azure"``.
    """

    target_type = "cloud"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        provider = target.extra.get("provider", "aws")
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported cloud provider {provider!r}. Must be one of: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
            )

        if target.dry_run:
            return [
                ResolvedAsset(
                    asset=target.value,
                    asset_type="cloud",
                    metadata={
                        "dry_run": True,
                        "provider": provider,
                        "action": "read-only IAM calls",
                    },
                )
            ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        provider = target.extra.get("provider", "aws")
        return f"[CLOUD] Will call read-only {provider.upper()} APIs (IAM, storage, compute) for: {target.value}"
