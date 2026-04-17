"""Pydantic models for Matadore findings, attack paths, and reports.

Every ``Vulnerability`` and ``AttackPath`` carries a mandatory
:class:`Evidence` field - the AI cannot assert a finding without a verifiable
source reference (port response, code line, API payload, etc.).
"""

from __future__ import annotations

from pydantic import BaseModel


class Evidence(BaseModel):
    """Verifiable source reference for a finding.

    Attributes:
        source: Where the evidence came from (e.g. ``"nmap scan"``,
            ``"git log a3f91c"``).
        detail: The raw data that substantiates the finding (packet capture
            excerpt, code snippet, API response body, etc.).
    """

    source: str
    detail: str


class Vulnerability(BaseModel):
    """A single security finding with mandatory evidence.

    Attributes:
        id: Unique finding identifier, e.g. ``"CVE-2024-23897"``.
        title: Short human-readable description.
        severity: ``"critical"``, ``"high"``, ``"medium"``, ``"low"``,
            or ``"info"``.
        evidence: Verifiable source reference - never empty.
        mitre_ttps: ATT&CK technique IDs applicable to this finding.
    """

    id: str
    title: str
    severity: str
    evidence: Evidence
    mitre_ttps: list[str] = []


class AttackPath(BaseModel):
    """A chained exploit sequence from initial access to impact.

    Attributes:
        narrative: Human-readable kill chain description.
        evidence: Source data that substantiates every step in the chain.
        mitre_ttps: Ordered ATT&CK technique IDs for each hop.
    """

    narrative: str
    evidence: Evidence
    mitre_ttps: list[str] = []


class Brief:
    """Narrative red team report generated from a :class:`Report`."""

    def to_markdown(self) -> str:
        """Return the brief as a Markdown string."""
        raise NotImplementedError

    def to_pdf(self) -> bytes:
        """Return the brief as a PDF byte string."""
        raise NotImplementedError


class Report:
    """Full engagement report returned by :meth:`~matadore.Matadore.engage`.

    Attributes:
        surface: All exposed assets discovered during the engagement.
        vulnerabilities: Findings ranked by exploitability, with evidence.
    """

    def __init__(self) -> None:
        self.surface: list[str] = []
        self.vulnerabilities: list[Vulnerability] = []

    def summary(self) -> str:
        """Return a one-paragraph executive summary of the engagement."""
        raise NotImplementedError

    def attack_paths(self) -> list[AttackPath]:
        """Return chained exploit sequences ordered by likelihood."""
        raise NotImplementedError

    def entry_points(self) -> list[str]:
        """Return the most likely initial access vectors."""
        raise NotImplementedError

    def shadow_it(self) -> list[str]:
        """Return assets not present in the known inventory."""
        raise NotImplementedError

    def what_would_they_hit_first(self) -> list[str]:
        """Return assets ranked by adversary priority."""
        raise NotImplementedError

    def brief(self) -> Brief:
        """Generate a narrative red team brief."""
        raise NotImplementedError

    def mitre_mapping(self) -> dict[str, list[str]]:
        """Return findings mapped to ATT&CK tactics and techniques."""
        raise NotImplementedError

    def remediation_plan(self) -> list[str]:
        """Return a prioritised fix list with effort estimates."""
        raise NotImplementedError

    def delta(self, previous: Report) -> Report:
        """Return a diff report showing what changed since *previous*."""
        raise NotImplementedError

    def audit_log(self) -> str:
        """Return a tamper-evident chain of custody for this engagement."""
        raise NotImplementedError

    def assert_no_new_criticals(self) -> None:
        """Raise if new critical findings were discovered.

        Use as a CI/CD gate::

            report.assert_no_new_criticals()
        """
        raise NotImplementedError

    def export(self, format: str, path: str | None = None) -> str:
        """Export the report to *format*.

        Args:
            format: ``"sarif"``, ``"asff"``, ``"markdown"``, or ``"pdf"``.
            path: Optional file path to write the output to.

        Returns:
            The exported content as a string (SARIF JSON, Markdown, etc.).
        """
        raise NotImplementedError
