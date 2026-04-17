"""Pydantic model for chained exploit sequences (kill chains)."""

from __future__ import annotations

from pydantic import BaseModel

from matadore.models.finding import Evidence


class AttackPath(BaseModel):
    """A chained exploit sequence from initial access to impact.

    Attributes:
        narrative: Human-readable kill chain description.
        evidence: Source data that substantiates every step in the chain.
        mitre_ttps: Ordered ATT&CK technique IDs for each hop.
        steps: Ordered list of asset/action pairs describing the path.
    """

    narrative: str
    evidence: Evidence
    mitre_ttps: list[str] = []
    steps: list[str] = []
