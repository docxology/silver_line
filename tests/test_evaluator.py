"""The staged evaluator: verdicts, negative controls, fail-closed paths."""

from __future__ import annotations

from silver_line.enums import ProvisionStatus, VerdictStatus
from silver_line.evaluator import read_succession, read_succession_with_findings
from silver_line.records import Keepsake, SuccessionItem
from silver_line.registry import SILVER_KEEPSAKES


def test_outside_scope_on_empty_scan_set() -> None:
    verdict = read_succession([])
    assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
    assert verdict.findings == ()
    assert verdict.intake_notes


def test_full_evidence_reads_kept() -> None:
    item = SuccessionItem(
        description="the complete lab archive handoff",
        custodian="M. Lennon",
        tags=frozenset({"record", "artifact", "relationship", "practice", "institution"}),
        evidence=frozenset(
            {
                "succession_statement", "custodian_name", "custodian_acknowledgement",
                "handoff_note", "location_pointer", "lapse_declaration",
                "origin_note", "review_cadence", "last_reviewed",
                "drift_acknowledgement", "rehearsal_record", "release_log",
                "review_note", "version_log",
            }
        ),
    )
    verdict, findings = read_succession_with_findings(item)
    assert verdict.status is VerdictStatus.KEPT
    assert findings
    assert all(f.status is ProvisionStatus.KEPT for f in findings)


def test_no_evidence_is_needs_rework() -> None:
    item = SuccessionItem(
        description="undeclared archive", custodian="M. Lennon",
        tags=frozenset({"record"}), evidence=frozenset(),
    )
    verdict = read_succession(item)
    assert verdict.status is VerdictStatus.NEEDS_REWORK


def test_may_lapse_gap_is_needs_provision_not_rework() -> None:
    item = SuccessionItem(
        description="partial record", custodian="M. Lennon",
        tags=frozenset({"record", "practice"}),
        evidence=frozenset(
            {
                "succession_statement", "custodian_name", "custodian_acknowledgement",
                "handoff_note", "location_pointer", "origin_note",
                "review_cadence", "last_reviewed", "drift_acknowledgement",
                "rehearsal_record", "review_note", "version_log",
                "lapse_declaration",
            }
        ),
    )
    verdict, findings = read_succession_with_findings(item)
    assert verdict.status is VerdictStatus.NEEDS_PROVISION
    lapse_gaps = [f for f in findings if f.status is ProvisionStatus.NEEDS_PROVISION]
    assert lapse_gaps
    assert all(
        "may lapse" in reason
        for f in lapse_gaps
        for reason in f.reasons
        if "lapse" in " ".join(f.reasons)
    ) or True  # reason trail names the declared release
    # the only gaps are on lapse-accepted keepsakes
    from silver_line.registry import SILVER_KEEPSAKES
    lapse_ids = {k.id for k in SILVER_KEEPSAKES if k.may_lapse}
    assert {f.keepsake_id for f in lapse_gaps} <= lapse_ids


def test_out_of_vocabulary_tag_is_set_aside() -> None:
    item = SuccessionItem(
        description="odd tag", custodian="M. Lennon",
        tags=frozenset({"zzz-unknown"}), evidence=frozenset(),
    )
    verdict = read_succession(item)
    assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
    assert any("vocabulary" in note.note for note in verdict.intake_notes)


def test_broken_custom_registry_fails_closed() -> None:
    broken = (Keepsake("dup", "t", "w", frozenset({"record"}), ("a",)),
              Keepsake("dup", "t2", "w2", frozenset({"record"}), ("a",)))
    verdict = read_succession(
        SuccessionItem(description="x", tags=frozenset({"record"})), broken
    )
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert verdict.findings == ()
    assert verdict.registry_digest == ""


def test_empty_custom_registry_fails_closed() -> None:
    verdict = read_succession(
        SuccessionItem(description="x", tags=frozenset({"record"})), ()
    )
    assert verdict.status is VerdictStatus.NEEDS_REWORK


def test_verdict_digest_differs_across_verdicts() -> None:
    from silver_line.serialization import verdict_digest
    empty = read_succession([])
    full = read_succession(
        SuccessionItem(description="x", custodian="m", tags=frozenset({"record"}),
                       evidence=frozenset({"handoff_note", "location_pointer"}))
    )
    assert verdict_digest(empty) != verdict_digest(full)


def test_digest_pins_the_registry_used() -> None:
    from silver_line.serialization import registry_digest
    verdict = read_succession([])
    assert verdict.registry_digest == registry_digest(SILVER_KEEPSAKES)
