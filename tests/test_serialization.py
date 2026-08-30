"""Deterministic serialization: sorted emit, byte-identical reruns."""

from __future__ import annotations

from silver_line.enums import IntakeDisposition, ProvisionStatus, VerdictStatus
from silver_line.records import IntakeNote, ProvisionFinding, SuccessionVerdict
from silver_line.serialization import (
    canonical_registry,
    canonical_verdict,
    registry_digest,
    verdict_digest,
)
from silver_line.registry import SILVER_KEEPSAKES


def test_canonical_registry_is_order_independent() -> None:
    forward = canonical_registry(SILVER_KEEPSAKES)
    reverse = canonical_registry(tuple(reversed(SILVER_KEEPSAKES)))
    assert forward == reverse


def test_registry_digest_changes_when_content_changes() -> None:
    altered = SILVER_KEEPSAKES + (
        SILVER_KEEPSAKES[0].__class__(**{**SILVER_KEEPSAKES[0].__dict__, "id": "zz-alt"}),)
    assert registry_digest(SILVER_KEEPSAKES) != registry_digest(altered)


def test_canonical_verdict_is_deterministic() -> None:
    verdict = SuccessionVerdict(
        VerdictStatus.NEEDS_REWORK,
        (ProvisionFinding("a", ProvisionStatus.NEEDS_REWORK, ("missing: x",)),),
        (IntakeNote(IntakeDisposition.SET_ASIDE, "set aside"),),
        "2026-08-29",
        "abc",
    )
    assert canonical_verdict(verdict) == canonical_verdict(verdict)
    assert len(verdict_digest(verdict)) == 64
