"""SQLite-backed state store for local single-user engagements.

Uses only the Python standard library -- no extra dependencies required.
The database file is created automatically on first use.

Usage::

    from matadore.state.sqlite import SQLiteStore

    store = SQLiteStore()                          # ~/.matadore/state.db
    store = SQLiteStore(path="/tmp/scan.db")       # custom path
    store = SQLiteStore(path=":memory:")           # in-memory (tests)
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from matadore.state.store import AssetSnapshot, StateStore

DEFAULT_DB_PATH = Path.home() / ".matadore" / "state.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS asset_snapshots (
    engagement_id TEXT NOT NULL,
    asset         TEXT NOT NULL,
    asset_type    TEXT NOT NULL,
    scanned_at    TEXT NOT NULL,
    checksum      TEXT NOT NULL DEFAULT '',
    raw           TEXT NOT NULL DEFAULT '',
    metadata      TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (engagement_id, asset)
)
"""


def _row_to_snapshot(row: sqlite3.Row) -> AssetSnapshot:
    return AssetSnapshot(
        engagement_id=row["engagement_id"],
        asset=row["asset"],
        asset_type=row["asset_type"],
        scanned_at=datetime.fromisoformat(row["scanned_at"]),
        checksum=row["checksum"],
        raw=row["raw"],
        metadata=json.loads(row["metadata"]),
    )


class SQLiteStore(StateStore):
    """Local SQLite-backed state store.

    Args:
        path: Path to the SQLite database file.  Pass ``":memory:"`` for an
            in-process store (useful in tests).  Defaults to
            ``~/.matadore/state.db``.
    """

    def __init__(self, path: str | Path = DEFAULT_DB_PATH) -> None:
        self._path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_CREATE_TABLE)
        self._conn.commit()

    def save_snapshot(self, snapshot: AssetSnapshot) -> None:
        self._conn.execute(
            """
            INSERT INTO asset_snapshots
                (engagement_id, asset, asset_type, scanned_at, checksum, raw, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(engagement_id, asset) DO UPDATE SET
                asset_type = excluded.asset_type,
                scanned_at = excluded.scanned_at,
                checksum   = excluded.checksum,
                raw        = excluded.raw,
                metadata   = excluded.metadata
            """,
            (
                snapshot.engagement_id,
                snapshot.asset,
                snapshot.asset_type,
                snapshot.scanned_at.isoformat(),
                snapshot.checksum,
                snapshot.raw,
                json.dumps(snapshot.metadata),
            ),
        )
        self._conn.commit()

    def get_snapshot(self, engagement_id: str, asset: str) -> AssetSnapshot | None:
        row = self._conn.execute(
            "SELECT * FROM asset_snapshots WHERE engagement_id = ? AND asset = ?",
            (engagement_id, asset),
        ).fetchone()
        return _row_to_snapshot(row) if row else None

    def list_snapshots(self, engagement_id: str) -> list[AssetSnapshot]:
        rows = self._conn.execute(
            "SELECT * FROM asset_snapshots WHERE engagement_id = ? ORDER BY scanned_at DESC",
            (engagement_id,),
        ).fetchall()
        return [_row_to_snapshot(r) for r in rows]

    def delete_engagement(self, engagement_id: str) -> None:
        self._conn.execute(
            "DELETE FROM asset_snapshots WHERE engagement_id = ?",
            (engagement_id,),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def checksum(raw: str) -> str:
        """Return a SHA-256 hex digest of *raw* for change detection."""
        return hashlib.sha256(raw.encode()).hexdigest()
