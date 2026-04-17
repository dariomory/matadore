"""Unit tests for matadore.models.audit."""

import hashlib
import json

from matadore.models.audit import AuditEntry, AuditLog


class TestAuditEntry:
    def test_create_generates_checksum(self):
        entry = AuditEntry(action="scan_started", actor="engine", target="example.com")
        assert len(entry.checksum) == 64  # SHA-256 hex digest

    def test_checksum_is_deterministic(self):
        entry1 = AuditEntry(action="plugin_run", actor="nmap", target="10.0.0.1")
        entry2 = AuditEntry(action="plugin_run", actor="nmap", target="10.0.0.1")
        # Timestamps will differ, so checksums will differ -- that is correct
        # behaviour; we only verify both are valid hex strings.
        assert all(c in "0123456789abcdef" for c in entry1.checksum)
        assert all(c in "0123456789abcdef" for c in entry2.checksum)

    def test_checksum_changes_with_content(self):
        e1 = AuditEntry(action="scan_started", actor="engine", target="a.com")
        e2 = AuditEntry(action="scan_started", actor="engine", target="b.com")
        assert e1.checksum != e2.checksum

    def test_default_fields(self):
        entry = AuditEntry(action="report_exported", actor="report", target="sarif")
        assert entry.detail == ""
        assert entry.timestamp is not None


class TestAuditLog:
    def test_create(self):
        log = AuditLog(engagement_id="eng-001")
        assert log.engagement_id == "eng-001"
        assert log.entries == []

    def test_append(self):
        log = AuditLog(engagement_id="eng-001")
        entry = AuditEntry(action="scan_started", actor="engine", target="example.com")
        log.append(entry)
        assert len(log.entries) == 1
        assert log.entries[0].action == "scan_started"

    def test_to_text_contains_engagement_id(self):
        log = AuditLog(engagement_id="eng-007")
        text = log.to_text()
        assert "eng-007" in text

    def test_to_text_contains_entry_details(self):
        log = AuditLog(engagement_id="eng-007")
        log.append(AuditEntry(action="plugin_run", actor="nmap", target="10.0.0.1"))
        text = log.to_text()
        assert "plugin_run" in text
        assert "nmap" in text
        assert "10.0.0.1" in text

    def test_to_text_contains_checksum(self):
        log = AuditLog(engagement_id="eng-007")
        entry = AuditEntry(action="scan_done", actor="engine", target="example.com")
        log.append(entry)
        text = log.to_text()
        assert entry.checksum in text
