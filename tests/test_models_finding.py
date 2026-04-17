"""Unit tests for matadore.models.finding."""

import pytest
from pydantic import ValidationError

from matadore.models.finding import Evidence, RawFinding, Vulnerability


class TestEvidence:
    def test_create(self):
        e = Evidence(source="nmap scan", detail="port 22 open")
        assert e.source == "nmap scan"
        assert e.detail == "port 22 open"

    def test_missing_source_raises(self):
        with pytest.raises(ValidationError):
            Evidence(detail="some detail")  # type: ignore

    def test_missing_detail_raises(self):
        with pytest.raises(ValidationError):
            Evidence(source="nmap scan")  # type: ignore

    def test_serialises_to_dict(self):
        e = Evidence(source="api response", detail="{}")
        d = e.model_dump()
        assert d == {"source": "api response", "detail": "{}"}


class TestRawFinding:
    def test_create(self):
        rf = RawFinding(plugin="nmap", asset="192.168.1.1", raw="22/tcp open ssh")
        assert rf.plugin == "nmap"
        assert rf.asset == "192.168.1.1"
        assert rf.raw == "22/tcp open ssh"

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            RawFinding(plugin="nmap", asset="192.168.1.1")  # type: ignore

    def test_serialises_to_dict(self):
        rf = RawFinding(plugin="trivy", asset="myorg/myimage", raw="CVE-2024-1234")
        d = rf.model_dump()
        assert d["plugin"] == "trivy"
        assert d["asset"] == "myorg/myimage"


class TestVulnerability:
    def _evidence(self) -> Evidence:
        return Evidence(source="nmap", detail="port 443 open, TLS 1.0 detected")

    def test_create_minimal(self):
        v = Vulnerability(
            id="CVE-2024-9999",
            title="Weak TLS version",
            severity="high",
            evidence=self._evidence(),
        )
        assert v.id == "CVE-2024-9999"
        assert v.severity == "high"
        assert v.mitre_ttps == []
        assert v.asset == ""

    def test_create_full(self):
        v = Vulnerability(
            id="CVE-2024-9999",
            title="Weak TLS version",
            severity="high",
            asset="api.example.com",
            evidence=self._evidence(),
            mitre_ttps=["T1190", "T1071"],
        )
        assert v.asset == "api.example.com"
        assert v.mitre_ttps == ["T1190", "T1071"]

    def test_evidence_is_required(self):
        with pytest.raises(ValidationError):
            Vulnerability(id="CVE-X", title="X", severity="low")  # type: ignore

    def test_evidence_nested_access(self):
        v = Vulnerability(
            id="CVE-2024-9999",
            title="Weak TLS version",
            severity="high",
            evidence=self._evidence(),
        )
        assert v.evidence.source == "nmap"

    def test_serialises_to_dict(self):
        v = Vulnerability(
            id="CVE-2024-9999",
            title="Weak TLS",
            severity="medium",
            evidence=self._evidence(),
        )
        d = v.model_dump()
        assert d["id"] == "CVE-2024-9999"
        assert "evidence" in d
        assert d["evidence"]["source"] == "nmap"
