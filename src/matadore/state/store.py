"""Abstract state store interface for engagement caching and diff scanning.

Matadore caches engagement state so repeated scans only re-process assets
that have changed.  Two concrete backends are provided:

- :class:`~matadore.state.sqlite.SQLiteStore` -- local single-user store
- :class:`~matadore.state.duckdb.DuckDBStore` -- team-shared store

Both implement this interface, so the engine stays decoupled from storage.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AssetSnapshot:
    """Immutable record of an asset's state at scan time.

    Attributes:
        engagement_id: The engagement this snapshot belongs to.
        asset: Asset identifier (domain, IP, repo slug, etc.).
        asset_type: Fine-grained type label (``"ip"``, ``"url"``, etc.).
        scanned_at: UTC timestamp of the scan.
        checksum: SHA-256 of the raw plugin output for change detection.
        raw: Raw plugin output stored for diff analysis.
        metadata: Additional structured data about the asset.
    """

    engagement_id: str
    asset: str
    asset_type: str
    scanned_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    checksum: str = ""
    raw: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class StateStore(abc.ABC):
    """Abstract persistence layer for engagement state.

    Implementations must be safe to use across concurrent asyncio tasks
    within a single process.
    """

    @abc.abstractmethod
    def save_snapshot(self, snapshot: AssetSnapshot) -> None:
        """Persist *snapshot* for the given asset.

        If a snapshot for the same ``(engagement_id, asset)`` pair already
        exists it is overwritten.

        Args:
            snapshot: The asset state to persist.
        """

    @abc.abstractmethod
    def get_snapshot(self, engagement_id: str, asset: str) -> AssetSnapshot | None:
        """Return the most recent snapshot for *asset* in *engagement_id*.

        Args:
            engagement_id: Engagement identifier.
            asset: Asset identifier.

        Returns:
            The stored :class:`AssetSnapshot`, or ``None`` if not found.
        """

    @abc.abstractmethod
    def list_snapshots(self, engagement_id: str) -> list[AssetSnapshot]:
        """Return all snapshots for *engagement_id*.

        Args:
            engagement_id: Engagement identifier.

        Returns:
            Ordered list of :class:`AssetSnapshot` objects, newest first.
        """

    @abc.abstractmethod
    def delete_engagement(self, engagement_id: str) -> None:
        """Remove all stored state for *engagement_id*.

        Args:
            engagement_id: Engagement identifier to purge.
        """

    def has_changed(self, snapshot: AssetSnapshot) -> bool:
        """Return ``True`` if *snapshot* differs from the stored version.

        Uses checksum comparison when available, otherwise always returns
        ``True`` (forcing a re-scan).

        Args:
            snapshot: The freshly computed snapshot to compare.
        """
        stored = self.get_snapshot(snapshot.engagement_id, snapshot.asset)
        if stored is None:
            return True
        if not snapshot.checksum or not stored.checksum:
            return True
        return snapshot.checksum != stored.checksum

    def close(self) -> None:  # noqa: B027
        """Release any held resources (connections, file handles, etc.).

        The default implementation is a no-op.  Override in backends that
        hold open connections.
        """
