"""Input handler for Docker registry / container image targets."""

from __future__ import annotations

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class DockerRegistryInput(BaseInput):
    """Pulls metadata for a container image to scan for embedded credentials
    and vulnerable dependencies.

    Does not run the image -- only analyses the layer manifest and filesystem.

    Target type: ``docker_registry``
    """

    target_type = "docker_registry"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        if target.dry_run:
            return [
                ResolvedAsset(
                    asset=target.value,
                    asset_type="docker_image",
                    metadata={
                        "dry_run": True,
                        "action": "pull manifest + analyse layers (read-only)",
                    },
                )
            ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        return (
            f"[DOCKER] Will pull manifest and scan layers for: {target.value} "
            f"(embedded credentials, vulnerable packages)"
        )
