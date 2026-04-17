"""Pydantic models for individual security findings.

Every :class:`Vulnerability` carries a mandatory :class:`Evidence` field -
the AI cannot assert a finding without a verifiable source reference (port
response, code line, API payload, etc.).
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


class RawFinding(BaseModel):
    """Unprocessed output from a scanner plugin before LLM reasoning.

    Attributes:
        plugin: Name of the plugin that produced this finding.
        asset: The target asset (IP, URL, repo path, etc.).
        raw: Raw output string from the underlying tool.
    """

    plugin: str
    asset: str
    raw: str


class Vulnerability(BaseModel):
    """A single security finding with mandatory evidence.

    Attributes:
        id: Unique finding identifier, e.g. ``"CVE-2024-23897"``.
        title: Short human-readable description.
        severity: ``"critical"``, ``"high"``, ``"medium"``, ``"low"``,
            or ``"info"``.
        asset: The target asset this vulnerability was found on.
        evidence: Verifiable source reference - never empty.
        mitre_ttps: ATT&CK technique IDs applicable to this finding.
    """

    id: str
    title: str
    severity: str
    asset: str = ""
    evidence: Evidence
    mitre_ttps: list[str] = []
