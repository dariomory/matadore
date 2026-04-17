"""DuckDB-backed state store for team-shared engagement state.

DuckDB is an optional dependency -- install it with::

    pip install duckdb

This backend is designed for teams that share a single persistent store
(e.g. on a network file share or an object-storage-mounted path) so that
multiple operators can see each other's engagement history and diff results.

Usage::

    from matadore.state.duckdb import DuckDBStore

    store = DuckDBStore(path="/shared/matadore/state.duckdb")
    store = DuckDBStore(path=":memory:")   # in-memory (tests)
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from matadore.state.store import AssetSnapshot, StateStore

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS asset_snapshots (
    engagement_id VARCHAR NOT NULL,
    asset         VARCHAR NOT NULL,
    asset_type    VARCHAR NOT NULL,
    scanned_at    TIMESTAMPTZ NOT NULL,
    checksum      VARCHAR NOT NULL DEFAULT '',
    raw           VARCHAR NOT NULL DEFAULT '',
    metadata      VARCHAR NOT NULL DEFAULT '{}',
    PRIMARY KEY (engagement_id, asset)
)
"""


class DuckDBStore(StateStore):
    """Team-shared DuckDB-backed state store.

    Requires ``duckdb`` to be installed.  Raises :class:`ImportError` with a
    helpful message if it is not available.

    Args:
        path: Path to the DuckDB database file.  Pass ``":memory:"`` for an
            in-process store (useful in tests).
    """

    def __init__(self, path: str | Path = ":memory:") -> None:
        try:
            import duckdb  # noqa: PLC0415  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError("DuckDBStore requires the 'duckdb' package. Install it with: pip install duckdb") from exc

        self._duckdb = duckdb
        self._conn = duckdb.connect(str(path))
        self._conn.execute(_CREATE_TABLE)

    def _row_to_snapshot(self, row: Any) -> AssetSnapshot:
        engagement_id, asset, asset_type, scanned_at, checksum, raw, metadata = row
        return AssetSnapshot(
            engagement_id=engagement_id,
            asset=asset,
            asset_type=asset_type,
            scanned_at=scanned_at if isinstance(scanned_at, datetime) else datetime.fromisoformat(str(scanned_at)),
            checksum=checksum,
            raw=raw,
            metadata=json.loads(metadata) if isinstance(metadata, str) else metadata,
        )

    def save_snapshot(self, snapshot: AssetSnapshot) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO asset_snapshots
                (engagement_id, asset, asset_type, scanned_at, checksum, raw, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.engagement_id,
                snapshot.asset,
                snapshot.asset_type,
                snapshot.scanned_at,
                snapshot.checksum,
                snapshot.raw,
                json.dumps(snapshot.metadata),
            ),
        )

    def get_snapshot(self, engagement_id: str, asset: str) -> AssetSnapshot | None:
        rows = self._conn.execute(
            "SELECT * FROM asset_snapshots WHERE engagement_id = ? AND asset = ?",
            [engagement_id, asset],
        ).fetchall()
        return self._row_to_snapshot(rows[0]) if rows else None

    def list_snapshots(self, engagement_id: str) -> list[AssetSnapshot]:
        rows = self._conn.execute(
            "SELECT * FROM asset_snapshots WHERE engagement_id = ? ORDER BY scanned_at DESC",
            [engagement_id],
        ).fetchall()
        return [self._row_to_snapshot(r) for r in rows]

    def delete_engagement(self, engagement_id: str) -> None:
        self._conn.execute(
            "DELETE FROM asset_snapshots WHERE engagement_id = ?",
            [engagement_id],
        )

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def checksum(raw: str) -> str:
        """Return a SHA-256 hex digest of *raw* for change detection."""
        return hashlib.sha256(raw.encode()).hexdigest()
