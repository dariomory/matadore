"""Unit tests for matadore.models.report."""

import pytest

from matadore.models.finding import Evidence, Vulnerability
from matadore.models.report import Brief, Report


def _vuln(severity: str = "high") -> Vulnerability:
    return Vulnerability(
        id="CVE-2024-0001",
        title="Test finding",
        severity=severity,
        evidence=Evidence(source="nmap", detail="port 22 open"),
    )


class TestReport:
    def test_create_empty(self):
        r = Report(engagement_id="eng-001")
        assert r.surface == []
        assert r.vulnerabilities == []

    def test_audit_log_contains_id(self):
        r = Report(engagement_id="eng-42")
        assert "eng-42" in r.audit_log()

    def test_surface_mutable(self):
        r = Report()
        r.surface.append("staging.example.com")
        assert "staging.example.com" in r.surface

    def test_vulnerabilities_mutable(self):
        r = Report()
        r.vulnerabilities.append(_vuln())
        assert len(r.vulnerabilities) == 1

    def test_unimplemented_methods_raise(self):
        r = Report()
        for method in (
            "summary",
            "attack_paths",
            "entry_points",
            "shadow_it",
            "what_would_they_hit_first",
            "brief",
            "mitre_mapping",
            "remediation_plan",
            "assert_no_new_criticals",
        ):
            with pytest.raises(NotImplementedError):
                getattr(r, method)()

    def test_export_raises(self):
        r = Report()
        with pytest.raises(NotImplementedError):
            r.export("sarif")

    def test_delta_raises(self):
        r1 = Report()
        r2 = Report()
        with pytest.raises(NotImplementedError):
            r1.delta(r2)


class TestBrief:
    def test_to_markdown_raises(self):
        b = Brief()
        with pytest.raises(NotImplementedError):
            b.to_markdown()

    def test_to_pdf_raises(self):
        b = Brief()
        with pytest.raises(NotImplementedError):
            b.to_pdf()
