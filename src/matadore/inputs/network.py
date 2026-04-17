"""Input handler for network range (CIDR) targets."""

from __future__ import annotations

import ipaddress

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class NetworkInput(BaseInput):
    """Expands a CIDR range into individual host IP addresses.

    Broadcast and network addresses (.0 and .255 for /24) are automatically
    excluded.

    Target type: ``network``
    """

    target_type = "network"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        if target.dry_run:
            try:
                network = ipaddress.ip_network(target.value, strict=False)
                hosts = list(network.hosts())
                return [
                    ResolvedAsset(
                        asset=target.value,
                        asset_type="network",
                        metadata={"host_count": len(hosts), "dry_run": True},
                    )
                ]
            except ValueError:
                return [
                    ResolvedAsset(
                        asset=target.value,
                        asset_type="network",
                        metadata={"dry_run": True},
                    )
                ]
        raise NotImplementedError

    def describe(self, target: EngageTarget) -> str:
        try:
            network = ipaddress.ip_network(target.value, strict=False)
            hosts = list(network.hosts())
            return f"[NETWORK] Will probe {len(hosts)} hosts in {target.value} (skipping .0/broadcast)"
        except ValueError:
            return f"[NETWORK] Will probe: {target.value}"
