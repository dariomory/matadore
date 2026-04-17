"""Report and Brief models returned by an engagement."""

from __future__ import annotations

from matadore.models.attack_path import AttackPath
from matadore.models.audit import AuditLog
from matadore.models.finding import Vulnerability


class Brief:
    """Narrative red team report generated from a :class:`Report`."""

    def __init__(self, text: str = "") -> None:
        self._text = text

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
        _audit: Internal audit log for this engagement.
    """

    def __init__(self, engagement_id: str = "") -> None:
        self.surface: list[str] = []
        self.vulnerabilities: list[Vulnerability] = []
        self._audit = AuditLog(engagement_id=engagement_id)

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
        return self._audit.to_text()

    def assert_no_new_criticals(self) -> None:
        """Raise if new critical findings were discovered.

        Use as a CI/CD gate::

            report.assert_no_new_criticals()
        """
        raise NotImplementedError

    def export(self, format: str, path: str | None = None) -> str:  # noqa: A002
        """Export the report to *format*.

        Args:
            format: ``"sarif"``, ``"asff"``, ``"markdown"``, or ``"pdf"``.
            path: Optional file path to write the output to.

        Returns:
            The exported content as a string (SARIF JSON, Markdown, etc.).
        """
        raise NotImplementedError
