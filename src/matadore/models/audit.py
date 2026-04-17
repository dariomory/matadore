"""Audit log models for tamper-evident chain of custody."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """A single immutable record in the engagement audit trail.

    Attributes:
        timestamp: UTC timestamp of the event.
        action: Short action label (e.g. ``"scan_started"``, ``"plugin_run"``).
        actor: Who or what performed the action (plugin name, ``"llm"``, etc.).
        target: The asset or resource the action was performed against.
        detail: Free-form detail string for human review.
        checksum: SHA-256 of the entry fields for tamper detection.
    """

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: str
    actor: str
    target: str
    detail: str = ""
    checksum: str = ""

    def model_post_init(self, __context: object) -> None:  # noqa: ANN001
        if not self.checksum:
            payload = json.dumps(
                {
                    "timestamp": self.timestamp.isoformat(),
                    "action": self.action,
                    "actor": self.actor,
                    "target": self.target,
                    "detail": self.detail,
                },
                sort_keys=True,
            )
            object.__setattr__(
                self, "checksum", hashlib.sha256(payload.encode()).hexdigest()
            )


class AuditLog(BaseModel):
    """Ordered, tamper-evident chain of custody for an engagement.

    Attributes:
        engagement_id: Unique identifier for this engagement run.
        entries: Ordered list of audit entries.
    """

    engagement_id: str
    entries: list[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        """Append *entry* to the log."""
        self.entries.append(entry)

    def to_text(self) -> str:
        """Return a human-readable audit trail."""
        lines = [f"Engagement: {self.engagement_id}", ""]
        for e in self.entries:
            lines.append(
                f"[{e.timestamp.isoformat()}] {e.action} | {e.actor} → {e.target}"
            )
            if e.detail:
                lines.append(f"  {e.detail}")
            lines.append(f"  checksum: {e.checksum}")
        return "\n".join(lines)
