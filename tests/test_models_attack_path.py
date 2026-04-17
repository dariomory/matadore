"""Unit tests for matadore.models.attack_path."""

import pytest
from pydantic import ValidationError

from matadore.models.attack_path import AttackPath
from matadore.models.finding import Evidence


def _evidence() -> Evidence:
    return Evidence(source="git log", detail="AWS key in commit a3f91c")


class TestAttackPath:
    def test_create_minimal(self):
        ap = AttackPath(narrative="Attacker uses exposed key.", evidence=_evidence())
        assert ap.narrative == "Attacker uses exposed key."
        assert ap.mitre_ttps == []
        assert ap.steps == []

    def test_create_full(self):
        ap = AttackPath(
            narrative="Initial access via Jenkins CVE, pivot to S3.",
            evidence=_evidence(),
            mitre_ttps=["T1190", "T1078", "T1530"],
            steps=["Jenkins RCE", "Extract IAM key", "s3:GetObject"],
        )
        assert len(ap.mitre_ttps) == 3
        assert ap.steps[0] == "Jenkins RCE"

    def test_evidence_required(self):
        with pytest.raises(ValidationError):
            AttackPath(narrative="some narrative")  # type: ignore[call-arg]

    def test_serialises_to_dict(self):
        ap = AttackPath(narrative="Kill chain.", evidence=_evidence())
        d = ap.model_dump()
        assert d["narrative"] == "Kill chain."
        assert d["evidence"]["source"] == "git log"
