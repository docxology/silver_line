from dataclasses import replace
from enum import Enum

import pytest

from silver_line import SuccessionItem, VerdictStatus, read_succession
from silver_line.records import Keepsake
from silver_line.registry import SILVER_KEEPSAKES


def complete_item():
    return SuccessionItem(
        "notebooks", "successor", frozenset({"record"}),
        frozenset(label for k in SILVER_KEEPSAKES for label in k.required_evidence),
    )


@pytest.mark.parametrize("custodian", ["", "  ", None, 42])
def test_sl01_missing_custody_cannot_be_offset(custodian):
    broken = replace(complete_item(), custodian=custodian)
    verdict = read_succession([broken, complete_item()])
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert any("custodian" in r for f in verdict.findings for r in f.reasons)


def test_sl01_name_without_acknowledgement_is_still_a_gap():
    item = replace(complete_item(), evidence=complete_item().evidence - {"custodian_acknowledgement"})
    assert read_succession(item).status is VerdictStatus.NEEDS_REWORK


def test_sl02_unknown_custom_registry_cannot_match():
    registry = (Keepsake("custom", "title", "wire", frozenset({"zzz-unknown"}), ("a",)),)
    item = SuccessionItem("x", "successor", frozenset({"zzz-unknown"}), frozenset({"a"}))
    verdict = read_succession(item, registry)
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert not verdict.findings


def test_sl02_unknown_tags_are_actually_filtered():
    from silver_line.evaluator import _prepare
    items, notes, _ = _prepare(replace(complete_item(), tags=frozenset({"record", "zzz-unknown"})))
    assert items[0].tags == frozenset({"record"})
    assert any("did not match" in n.note for n in notes)


def test_sl03_silence_is_not_a_declared_release():
    verdict = read_succession(replace(complete_item(), evidence=frozenset()))
    assert not any("declared release" in r for f in verdict.findings for r in f.reasons)
    lapse = next(f for f in verdict.findings if f.keepsake_id == "lapse-named")
    assert any("not yet declared" in r for r in lapse.reasons)


def test_sl03_restraint_is_not_lapse_eligible():
    item = replace(complete_item(), evidence=complete_item().evidence - {"drift_acknowledgement"})
    assert read_succession(item).status is VerdictStatus.NEEDS_REWORK


class OtherKind(str, Enum):
    RETENTION = "RETENTION"


@pytest.mark.parametrize("changes", [
    {"kind": OtherKind.RETENTION},
    {"required_evidence": (" A ",)},
    {"required_evidence": ("a", "a")},
])
def test_p2_registry_contract_is_explicit(changes):
    registry = (replace(SILVER_KEEPSAKES[0], **changes),)
    verdict = read_succession(complete_item(), registry)
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert not verdict.findings
