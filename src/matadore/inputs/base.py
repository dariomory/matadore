"""Base class and target model for all Matadore input handlers.

Each target type supported by ``m.engage(target, type=...)`` maps to a
dedicated :class:`BaseInput` subclass.  The engine resolves the correct
handler at runtime based on the ``type`` field of :class:`EngageTarget`.

Example custom handler::

    from matadore.inputs.base import BaseInput, EngageTarget

    class SlackInput(BaseInput):
        target_type = "slack_workspace"

        def resolve(self, target: EngageTarget) -> list[str]:
            ...
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Literal

TARGET_TYPES = Literal[
    "domain",
    "network",
    "repo",
    "github_org",
    "cloud",
    "docker_registry",
]

SCAN_MODES = Literal["passive", "active", "stealth"]


@dataclass
class EngageTarget:
    """Parsed representation of a single engagement target.

    Attributes:
        value: Raw target string (domain, IP range, repo slug, etc.).
        type: Target category -- one of the ``TARGET_TYPES`` literals.
        mode: Scan aggressiveness -- ``"passive"``, ``"active"``, or
            ``"stealth"``.
        dry_run: When ``True`` no network traffic is generated.
        stream: When ``True`` findings are yielded as they arrive.
        extra: Additional kwargs forwarded from ``engage()`` (e.g.
            ``provider="aws"`` for cloud targets).
    """

    value: str
    type: str = "domain"
    mode: str = "active"
    dry_run: bool = False
    stream: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        valid = {"domain", "network", "repo", "github_org", "cloud", "docker_registry"}
        if self.type not in valid:
            raise ValueError(f"Unknown target type {self.type!r}. Must be one of: {', '.join(sorted(valid))}")
        valid_modes = {"passive", "active", "stealth"}
        if self.mode not in valid_modes:
            raise ValueError(f"Unknown scan mode {self.mode!r}. Must be one of: {', '.join(sorted(valid_modes))}")


@dataclass
class ResolvedAsset:
    """A single concrete asset discovered during target resolution.

    Attributes:
        asset: Asset identifier (IP address, URL, file path, etc.).
        asset_type: Fine-grained type label (e.g. ``"ip"``, ``"url"``,
            ``"s3_bucket"``).
        metadata: Optional structured data about the asset.
    """

    asset: str
    asset_type: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseInput(abc.ABC):
    """Abstract base for all target type handlers.

    Subclass this to add support for a new target type.

    Class attributes:
        target_type: The ``type=`` string this handler is responsible for.
    """

    target_type: str = "base"

    @abc.abstractmethod
    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        """Expand *target* into a flat list of concrete assets to scan.

        For a domain this might return the apex domain plus all discovered
        subdomains.  For a network range it returns individual host IPs.

        Args:
            target: The parsed engagement target.

        Returns:
            A list of :class:`ResolvedAsset` objects ready for plugin runs.
        """

    async def resolve_async(self, target: EngageTarget) -> list[ResolvedAsset]:
        """Async wrapper around :meth:`resolve`.

        Override for handlers that perform async I/O (DNS queries, GitHub
        API calls, etc.).  The default implementation wraps the sync method.
        """
        return self.resolve(target)

    def describe(self, target: EngageTarget) -> str:
        """Return a human-readable dry-run description of what would be done.

        Used by the planner to build the ``dry_run=True`` preview.

        Args:
            target: The parsed engagement target.

        Returns:
            A short sentence describing the planned action.
        """
        return f"[{self.target_type.upper()}] Will resolve: {target.value}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} target_type={self.target_type!r}>"
