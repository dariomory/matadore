"""Verify that the models package re-exports every public symbol."""

from matadore import models
from matadore.models import (
    AttackPath,
    AuditEntry,
    AuditLog,
    Brief,
    Evidence,
    RawFinding,
    Report,
    StreamEvent,
    Vulnerability,
)


def test_all_exports_importable():
    for name in [
        "AttackPath",
        "AuditEntry",
        "AuditLog",
        "Brief",
        "Evidence",
        "RawFinding",
        "Report",
        "StreamEvent",
        "Vulnerability",
    ]:
        assert hasattr(models, name), f"models.{name} not found"


def test_evidence_class():
    assert Evidence.__name__ == "Evidence"


def test_vulnerability_class():
    assert Vulnerability.__name__ == "Vulnerability"


def test_raw_finding_class():
    assert RawFinding.__name__ == "RawFinding"


def test_attack_path_class():
    assert AttackPath.__name__ == "AttackPath"


def test_stream_event_class():
    assert StreamEvent.__name__ == "StreamEvent"


def test_audit_entry_class():
    assert AuditEntry.__name__ == "AuditEntry"


def test_audit_log_class():
    assert AuditLog.__name__ == "AuditLog"


def test_report_class():
    assert Report.__name__ == "Report"


def test_brief_class():
    assert Brief.__name__ == "Brief"
