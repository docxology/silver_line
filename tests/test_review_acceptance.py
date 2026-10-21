from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from silver_line import ReleaseDeclaration, VerdictStatus, read_succession
from silver_line.artifacts import artifact_payloads, build_artifacts, build_envelope, fixture_items, validate_envelope
from silver_line.records import SuccessionVerdict
from silver_line.serialization import canonical_verdict, canonical_verdict_v1, verdict_digest
from silver_line.snapshots import canonical_source, source_value
from silver_line.validation import validate_review_date

ROOT = Path(__file__).resolve().parents[1]


def complete():
    fixture = json.loads((ROOT / "data/fixtures/silver_line_same_subject.json").read_text())
    return fixture_items(fixture)[0]


def test_explicit_release_preserves_restraint_and_item_scope():
    item = replace(complete(), evidence=frozenset({"drift_acknowledgement"}), custodian="")
    release = ReleaseDeclaration(item.item_id, "declared authority", "2026-10-19", "synthetic:release-record")
    item = replace(item, release=release)
    verdict = read_succession([item, replace(complete(), item_id="other")], evaluated_as_of="2026-10-20")
    assert verdict.status is VerdictStatus.DECLARED_RELEASE
    assert all(f.status.value == "KEPT" for f in verdict.findings if f.item_id == "other")
    assert any("explicit scoped release" in r for f in verdict.findings for r in f.reasons)
    assert any("no permission" in r for f in verdict.findings for r in f.reasons)
    assert read_succession(replace(item, evidence=frozenset())).status is VerdictStatus.NEEDS_REWORK
    assert "declared release" not in " ".join(r for f in read_succession(complete()).findings for r in f.reasons)


@pytest.mark.parametrize("release", [
    "release", ReleaseDeclaration("wrong", "a", "2026-10-19", "ref"),
    ReleaseDeclaration("register-handoff", "", "2026-10-19", "ref"),
    ReleaseDeclaration("register-handoff", "a", "bad-date", "ref"),
    ReleaseDeclaration("register-handoff", "a", "2026-10-21", "ref"),
])
def test_invalid_release_is_a_linked_gap(release):
    verdict = read_succession(replace(complete(), release=release), evaluated_as_of="2026-10-20")
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    finding = next(f for f in verdict.findings if f.keepsake_id == "release-declaration")
    assert finding.item_id == "register-handoff"
    assert finding.missing_fields == ("release",)


def test_release_without_applicable_eligibility_fails_closed():
    item = replace(complete(), tags=frozenset({"artifact"}), release=ReleaseDeclaration("register-handoff", "a", "2026-10-19", "ref"))
    verdict = read_succession(item)
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert any("no applicable lapse eligibility" in r for f in verdict.findings for r in f.reasons)


@pytest.mark.parametrize("value", [None, 42, "2026-02-30", "20261020", "2026-W43-2"])
def test_invalid_review_dates_raise_value_error(value):
    with pytest.raises(ValueError, match="review date"):
        read_succession([], evaluated_as_of=value)


def test_date_subject_and_source_are_bound():
    item = complete()
    a = read_succession(item, evaluated_as_of="2026-10-20", subject_id="a")
    b = read_succession(item, evaluated_as_of="2026-10-21", subject_id="a")
    c = read_succession(item, evaluated_as_of="2026-10-20", subject_id="b")
    assert len({verdict_digest(v) for v in (a, b, c)}) == 3
    assert verdict_digest(a) == verdict_digest(read_succession(item, evaluated_as_of="2026-10-20", subject_id="a"))
    assert json.loads(canonical_verdict(read_succession(item)))["date_mode"] == "UNDATED"
    for value in ("", "  ", None):
        with pytest.raises(ValueError, match="subject_id"):
            read_succession([], subject_id=value)
    spaced = read_succession(replace(item, custodian=" " + item.custodian))
    normal = read_succession(item)
    assert spaced.declaration_digest == normal.declaration_digest
    assert spaced.source_digest != normal.source_digest


def test_duplicate_ids_reject_entire_scan_and_counts_qualify_scope():
    item = complete()
    duplicate = read_succession([item, item])
    assert duplicate.status is VerdictStatus.NEEDS_REWORK
    assert not duplicate.findings
    assert duplicate.rejected_count == 2
    assert duplicate.intake_notes[0].item_id == item.item_id
    verdict = read_succession([item, None, replace(item, item_id="unknown", tags=frozenset({"unknown"}))])
    assert verdict.status is VerdictStatus.KEPT
    assert (verdict.accepted_count, verdict.rejected_count, verdict.unmatched_count) == (2, 1, 1)
    assert verdict.reading_scope == "PARTIAL"
    gap = read_succession(replace(item, custodian=""))
    assert any(f.item_id == item.item_id and "custodian" in f.missing_fields for f in gap.findings)


def test_rejected_declaration_keeps_its_declared_id_and_blocks_duplicates():
    item = complete()
    broken = replace(item, description="")
    for items in ([item, broken], [broken, item]):
        verdict = read_succession(items)
        assert verdict.status is VerdictStatus.NEEDS_REWORK
        assert not verdict.findings
        assert (verdict.accepted_count, verdict.rejected_count) == (0, 2)
        assert all(n.item_id == item.item_id for n in verdict.intake_notes if n.item_id)
        assert any(n.item_id == item.item_id and "description" in n.note for n in verdict.intake_notes)


def test_conflicting_duplicate_declarations_have_order_independent_rejection():
    alpha = replace(complete(), item_id="duplicate", description="alpha")
    beta = replace(alpha, description="beta")
    verdicts = [read_succession(items) for items in ([alpha, beta], [beta, alpha], {alpha, beta})]
    assert all(v.status is VerdictStatus.NEEDS_REWORK and not v.findings for v in verdicts)
    assert len({canonical_verdict(v) for v in verdicts}) == 1
    assert len({v.declaration_digest for v in verdicts}) == 1


def test_finite_container_boundary_and_normalization():
    assert read_succession(iter([complete()])).status is VerdictStatus.OUTSIDE_SCOPE
    assert read_succession(None).status is VerdictStatus.OUTSIDE_SCOPE
    for item in (replace(complete(), item_id=" bad "), replace(complete(), description="")):
        verdict = read_succession(item)
        assert verdict.rejected_count == 1
        assert any(n.item_id for n in verdict.intake_notes)
    verdict = read_succession(replace(complete(), tags=None, evidence=None))
    assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
    malformed = read_succession(replace(complete(), tags=frozenset({" Record ", None}), evidence=frozenset({42})))
    assert malformed.intake_notes
    assert canonical_source(complete())
    assert source_value(1.5) == 1.5
    assert "unsupported_type" in source_value(float("inf"))


def test_hash_seed_and_scan_permutations(tmp_path):
    program = "from silver_line import *; print(canonical_verdict(read_succession({SuccessionItem('a','x',frozenset({'record'})),SuccessionItem('b','y',frozenset({'artifact','unknown'}))})))"
    results = [subprocess.run([sys.executable, "-c", program], env={**os.environ, "PYTHONHASHSEED": seed},
                              check=True, text=True, capture_output=True).stdout for seed in ("1", "29", "104")]
    assert len(set(results)) == 1


def test_legacy_digest_verification_keeps_original_schema():
    payload = canonical_verdict_v1(SuccessionVerdict(VerdictStatus.OUTSIDE_SCOPE))
    assert json.loads(payload)["schema_version"] == "1.0"
    assert "subject_id" not in json.loads(payload)
    assert sha256(payload.encode()).hexdigest() != verdict_digest(SuccessionVerdict(VerdictStatus.OUTSIDE_SCOPE))


def test_every_envelope_field_has_a_negative_control():
    for path in sorted((ROOT / "data/fixtures").glob("*.json")):
        fixture = json.loads(path.read_text())
        envelope, files = artifact_payloads(fixture)
        verdict = read_succession(fixture_items(fixture), evaluated_as_of=fixture["review_date"], subject_id=fixture["subject_id"])
        refs = tuple(envelope["source_snapshot_refs"])
        validate_envelope(envelope, verdict, refs)
        for key in envelope:
            broken = {**envelope, key: "mutated"}
            with pytest.raises(ValueError, match="envelope differs"):
                validate_envelope(broken, verdict, refs)
            with pytest.raises(ValueError):
                validate_envelope({k: v for k, v in envelope.items() if k != key}, verdict, refs)
        report = files["data/reports/" + envelope["report_ref"] + ".json"]
        assert sha256(report.encode()).hexdigest() == envelope["report_ref"]
        assert json.loads(report)["subject_id"] == fixture["subject_id"]
        payload = json.loads(report)
        from silver_line.registry import SILVER_KEEPSAKES
        from silver_line.serialization import registry_digest
        from silver_line.version import __version__
        assert payload["evaluated_as_of"] == envelope["review_date"] == fixture["review_date"]
        assert payload["registry_digest"] == envelope["registry_digest"] == registry_digest(SILVER_KEEPSAKES)
        assert payload["registry_version"] == payload["evaluator_version"] == envelope["registry_version"] == __version__
        assert payload["status"] == envelope["native_status"]
        snapshot_hashes = {ref.split(":", 2)[1] for ref in refs}
        assert {payload["source_digest"], payload["declaration_digest"], payload["registry_digest"]} <= snapshot_hashes
        for ref in refs:
            scheme, digest, name = ref.split(":", 2)
            assert scheme == "sha256"
            assert sha256(files[name].encode()).hexdigest() == digest


def test_artifact_store_real_files_and_drift_controls(tmp_path):
    fixtures = tmp_path / "data/fixtures"
    fixtures.mkdir(parents=True)
    with pytest.raises(ValueError, match="no canonical fixtures"):
        build_artifacts(tmp_path, check=True)
    for path in (ROOT / "data/fixtures").glob("*.json"):
        (fixtures / path.name).write_bytes(path.read_bytes())
    outputs = build_artifacts(tmp_path)
    assert outputs == build_artifacts(tmp_path, check=True)
    assert outputs == build_artifacts(tmp_path)
    for name in outputs:
        path = tmp_path / name
        original = path.read_bytes()
        path.write_text("mutated")
        with pytest.raises(ValueError, match="artifact drift"):
            build_artifacts(tmp_path, check=True)
        if name.startswith(("data/reports/", "data/snapshots/")):
            with pytest.raises(ValueError, match="immutable artifact"):
                build_artifacts(tmp_path)
        path.write_bytes(original)
    (tmp_path / "data/envelopes/orphan.json").write_text("{}")
    with pytest.raises(ValueError, match="no canonical fixture"):
        build_artifacts(tmp_path, check=True)


def test_publishing_requires_date_subject_registry_and_sources():
    for verdict, refs in ((read_succession([]), ("ref",)),
                          (read_succession([], (), evaluated_as_of="2026-10-20", subject_id="s"), ("ref",)),
                          (read_succession([], evaluated_as_of="2026-10-20", subject_id="s"), ())):
        with pytest.raises(ValueError):
            build_envelope(verdict, refs)
    valid = read_succession(complete(), evaluated_as_of="2026-10-20", subject_id="s")
    with pytest.raises(ValueError, match="immutable SHA-256"):
        build_envelope(valid, ("mutable:path",))
    with pytest.raises(ValueError, match="bind registry"):
        build_envelope(valid, ("sha256:" + "a" * 64 + ":data/snapshots/" + "a" * 64 + ".json",))


def test_artifact_module_cli_checks_actual_store():
    result = subprocess.run([sys.executable, "-m", "silver_line.artifacts", "--check"], check=True, capture_output=True, text=True)
    assert "checked" in result.stdout


def test_empty_date_validation_is_explicit():
    assert validate_review_date("") == ""
