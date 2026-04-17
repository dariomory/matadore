"""Matadore domain models.

Re-exports the complete public model surface so callers can import from
either the sub-module or this package directly::

    from matadore.models import Evidence, Vulnerability, AttackPath, Report
"""

from matadore.models.attack_path import AttackPath
from matadore.models.audit import AuditEntry, AuditLog
from matadore.models.events import StreamEvent
from matadore.models.finding import Evidence, RawFinding, Vulnerability
from matadore.models.report import Brief, Report

__all__ = [
    "AttackPath",
    "AuditEntry",
    "AuditLog",
    "Brief",
    "Evidence",
    "RawFinding",
    "Report",
    "StreamEvent",
    "Vulnerability",
]
