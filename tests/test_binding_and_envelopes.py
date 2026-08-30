"""Binding declaration and witness envelopes: structure and field-set parity."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

#: Frozen copy of the witness envelope schema (field set of
#: witness_register/data/envelopes/black_line_worked.json), used when no
#: sibling checkout is present. Siblings are optional; absence is an outcome.
FROZEN_ENVELOPE_FIELDS = frozenset(
    {
        "line_id", "native_status", "registry_digest", "registry_version",
        "report_ref", "review_date", "schema_version", "scope_and_nonclaims",
        "source_snapshot_refs", "subject_id",
    }
)


def _sibling_envelope() -> dict | None:
    """Parse a real sibling envelope if present; else return None."""

    candidate = ROOT.parent / "witness_register" / "data" / "envelopes" / "black_line_worked.json"
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return None


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_binding_declaration_parses_and_matches_the_brief() -> None:
    binding = _json(DATA / "binding_declaration.json")
    assert binding["id"] == "silver_line"
    assert binding["color"] == "silver"
    assert binding["package_name"] == "silver_line"
    assert binding["opus_stage"] is None
    assert binding["working_position"] is None
    assert binding["must_not_become"]
    assert binding["question"]
    assert binding["job"]
    assert binding["registry_noun"]
    assert binding["verdict_noun"]


def test_worked_envelope_matches_field_set() -> None:
    envelope = _json(DATA / "envelopes" / "silver_line_worked.json")
    assert set(envelope) == FROZEN_ENVELOPE_FIELDS
    sibling = _sibling_envelope()
    if sibling is not None:
        assert set(envelope) == set(sibling)


def test_same_subject_envelope_matches_field_set() -> None:
    envelope = _json(DATA / "envelopes" / "silver_line_same_subject.json")
    assert set(envelope) == FROZEN_ENVELOPE_FIELDS
    sibling = _sibling_envelope()
    if sibling is not None:
        assert set(envelope) == set(sibling)


def test_worked_envelope_digest_matches_the_live_registry() -> None:
    from silver_line.serialization import registry_digest
    envelope = _json(DATA / "envelopes" / "silver_line_worked.json")
    assert envelope["registry_digest"] == registry_digest(__import__(
        "silver_line.registry", fromlist=["SILVER_KEEPSAKES"]
    ).SILVER_KEEPSAKES)


def test_envelopes_carry_scope_and_nonclaims() -> None:
    for name in ("silver_line_worked.json", "silver_line_same_subject.json"):
        envelope = _json(DATA / "envelopes" / name)
        assert envelope["scope_and_nonclaims"]
        assert envelope["schema_version"] == "line.report-envelope/1.0"
        assert envelope["line_id"] == "silver_line"
