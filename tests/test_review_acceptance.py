from dataclasses import asdict, replace
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from silver_line import (
    ReleaseDeclaration,
    VerdictStatus,
    read_succession,
    read_succession_with_findings,
)
from silver_line.artifacts import (
    artifact_payloads,
    build_artifacts,
    build_envelope,
    fixture_items,
    validate_envelope,
)
from silver_line.records import SuccessionVerdict
from silver_line.serialization import (
    canonical_verdict,
    canonical_verdict_v1,
    verdict_digest,
)
from silver_line.snapshots import restore_source
from silver_line.validation import validate_review_date

ROOT = Path(__file__).resolve().parents[1]


def complete():
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    return fixture_items(fixture)[0]


def matching_release_fixture():
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    row = fixture["items"][0]
    row["evidence"] = ["drift_acknowledgment"]
    row["release"] = asdict(
        ReleaseDeclaration(
            fixture["subject_id"],
            row["item_id"],
            "declared role",
            "2026-10-19",
            "synthetic:release-record",
        )
    )
    return fixture


def test_explicit_release_preserves_restraint_and_item_scope():
    item = replace(
        complete(), evidence=frozenset({"drift_acknowledgment"}), custodian=""
    )
    release = ReleaseDeclaration(
        "subject-a",
        item.item_id,
        "declared role",
        "2026-10-19",
        "synthetic:release-record",
    )
    item = replace(item, release=release)
    verdict = read_succession(
        [item, replace(complete(), item_id="other")],
        evaluated_as_of="2026-10-20",
        subject_id="subject-a",
    )
    assert verdict.status is VerdictStatus.DECLARED_RELEASE
    assert all(
        f.status.value == "KEPT" for f in verdict.findings if f.item_id == "other"
    )
    released = [f for f in verdict.findings if f.item_id == item.item_id]
    assert all(
        f.status.value
        == ("KEPT" if f.keepsake_id == "no-infallible-archive" else "DECLARED_RELEASE")
        for f in released
    )
    restrained = read_succession(
        replace(item, evidence=frozenset()), subject_id="subject-a"
    )
    assert restrained.status is VerdictStatus.NEEDS_REWORK
    gap = next(
        f for f in restrained.findings if f.keepsake_id == "no-infallible-archive"
    )
    assert gap.missing_fields == ("drift_acknowledgment",)
    assert any(f.status.value == "DECLARED_RELEASE" for f in restrained.findings)
    assert all(f.status.value == "KEPT" for f in read_succession(complete()).findings)


@pytest.mark.parametrize("api", [read_succession, read_succession_with_findings])
def test_release_cannot_cross_subjects_with_the_same_item_id(api):
    item = complete()
    item = replace(
        item,
        release=ReleaseDeclaration(
            "subject-a",
            item.item_id,
            "declared role",
            "2026-10-19",
            "synthetic:subject-a-release",
        ),
    )

    def read(subject):
        result = api(item, subject_id=subject, evaluated_as_of="2026-10-20")
        return result[0] if isinstance(result, tuple) else result

    matching = read("subject-a")
    assert matching.status is VerdictStatus.DECLARED_RELEASE
    for subject in ("subject-b", "UNSPECIFIED"):
        mismatched = read(subject)
        assert mismatched.status is VerdictStatus.NEEDS_REWORK
        assert mismatched.source_digest == matching.source_digest
        assert mismatched.declaration_digest == matching.declaration_digest
        assert verdict_digest(mismatched) != verdict_digest(matching)
        gap = next(
            f for f in mismatched.findings if f.keepsake_id == "release-declaration"
        )
        assert gap.item_id == item.item_id
        assert gap.missing_fields == ("release",)
        assert not any(
            f.status.value == "DECLARED_RELEASE" for f in mismatched.findings
        )


@pytest.mark.parametrize(
    "release",
    [
        "release",
        False,
        0,
        "",
        [],
        {},
        ReleaseDeclaration("subject-a", "wrong", "a", "2026-10-19", "ref"),
        ReleaseDeclaration("subject-a", "register-handoff", "", "2026-10-19", "ref"),
        ReleaseDeclaration("subject-a", "register-handoff", "a", "bad-date", "ref"),
        ReleaseDeclaration("subject-a", "register-handoff", "a", "2026-10-21", "ref"),
        ReleaseDeclaration("", "register-handoff", "a", "2026-10-19", "ref"),
        ReleaseDeclaration(" subject-a ", "register-handoff", "a", "2026-10-19", "ref"),
        ReleaseDeclaration(None, "register-handoff", "a", "2026-10-19", "ref"),
        ReleaseDeclaration("UNSPECIFIED", "register-handoff", "a", "2026-10-19", "ref"),
    ],
)
def test_invalid_release_is_a_linked_gap(release):
    verdict = read_succession(
        replace(complete(), release=release),
        evaluated_as_of="2026-10-20",
        subject_id="subject-a",
    )
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    finding = next(
        f for f in verdict.findings if f.keepsake_id == "release-declaration"
    )
    assert finding.item_id == "register-handoff"
    assert finding.missing_fields == ("release",)


def test_unspecified_subject_cannot_declare_release():
    item = replace(
        complete(),
        release=ReleaseDeclaration(
            "UNSPECIFIED",
            "register-handoff",
            "a",
            "2026-10-19",
            "ref",
        ),
    )
    verdict = read_succession(item)
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert not any(f.status.value == "DECLARED_RELEASE" for f in verdict.findings)


def test_release_without_applicable_eligibility_fails_closed():
    item = replace(
        complete(),
        tags=frozenset({"artifact"}),
        release=ReleaseDeclaration(
            "subject-a",
            "register-handoff",
            "a",
            "2026-10-19",
            "ref",
        ),
    )
    verdict = read_succession(item, subject_id="subject-a")
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert any(f.keepsake_id == "release-declaration" for f in verdict.findings)
    assert not any(f.status.value == "DECLARED_RELEASE" for f in verdict.findings)


@pytest.mark.parametrize(
    "release",
    [
        {},
        [],
        "",
        False,
        0,
        True,
        1,
        "release",
        ["release"],
        {
            "subject_id": "subject-a",
            "item_id": "register-handoff",
            "declared_by": "role",
            "declared_on": "2026-10-19",
            "source_ref": "synthetic:release",
            "unexpected": "not a declaration field",
        },
        {"item_id": "register-handoff"},
        {
            "item_id": "register-handoff",
            "declared_by": "role",
            "declared_on": "2026-10-19",
            "source_ref": "synthetic:legacy-release",
        },
    ],
)
def test_fixture_loader_rejects_explicit_malformed_release(release):
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    fixture["items"][0]["release"] = release
    with pytest.raises(ValueError, match="fixture release"):
        fixture_items(fixture)
    with pytest.raises(ValueError, match="fixture release"):
        artifact_payloads(fixture)


@pytest.mark.parametrize("field", ["tags", "evidence"])
@pytest.mark.parametrize(
    "bad",
    [
        {"record": False, "drift_acknowledgment": False},
        "drift_acknowledgment",
        ("record", "drift_acknowledgment"),
        {"record", "drift_acknowledgment"},
        frozenset({"record", "drift_acknowledgment"}),
        b"record",
        None,
        False,
        42,
    ],
)
def test_fixture_label_containers_cannot_manufacture_declarations(field, bad):
    fixture = matching_release_fixture()
    fixture["items"][0][field] = bad
    with pytest.raises(ValueError, match=rf"fixture {field}.*array"):
        fixture_items(fixture)
    with pytest.raises(ValueError, match=rf"fixture {field}.*array"):
        artifact_payloads(fixture)


@pytest.mark.parametrize("field", ["tags", "evidence"])
@pytest.mark.parametrize("check", [False, True])
def test_artifact_builder_refuses_label_object_keys_before_writing(
    tmp_path, field, check
):
    fixture = matching_release_fixture()
    row = fixture["items"][0]
    row[field] = dict.fromkeys(row[field], False)
    fixtures = tmp_path / "data/fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "release.json").write_text(json.dumps(fixture), encoding="utf-8")
    historical = next(iter(sorted((ROOT / "data/reports").glob("*.json"))))
    original = historical.read_bytes()
    retained = tmp_path / "data/reports" / historical.name
    retained.parent.mkdir()
    retained.write_bytes(original)

    with pytest.raises(ValueError, match=rf"fixture {field}.*array"):
        build_artifacts(tmp_path, check=check)

    assert retained.read_bytes() == original
    assert set(retained.parent.iterdir()) == {retained}
    assert not (tmp_path / "data/snapshots").exists()
    assert not (tmp_path / "data/envelopes").exists()


@pytest.mark.parametrize("field", ["tags", "evidence"])
@pytest.mark.parametrize("malformed", [None, False, 42, "", "\ud800"])
def test_fixture_arrays_keep_native_malformed_scalar_label_policy(field, malformed):
    fixture = matching_release_fixture()
    row = fixture["items"][0]
    row[field].append(malformed)
    items = fixture_items(fixture)
    assert getattr(items[0], field) == frozenset(row[field])
    verdict = read_succession(
        items,
        subject_id=fixture["subject_id"],
        evaluated_as_of=fixture["review_date"],
    )
    assert verdict.status is VerdictStatus.DECLARED_RELEASE
    assert verdict.intake_notes
    envelope, files = artifact_payloads(fixture)
    assert envelope["native_status"] == "DECLARED_RELEASE"
    assert files[f"data/reports/{envelope['report_ref']}.json"] == canonical_verdict(
        verdict
    )


@pytest.mark.parametrize(
    "evidence, status",
    [
        (["drift_acknowledgment"], "DECLARED_RELEASE"),
        ([], "NEEDS_REWORK"),
        ([None, False, 42, "", "\ud800"], "NEEDS_REWORK"),
    ],
)
def test_fixture_release_arrays_do_not_replace_restraint(evidence, status):
    fixture = matching_release_fixture()
    fixture["items"][0]["evidence"] = evidence
    envelope, files = artifact_payloads(fixture)
    report = json.loads(files[f"data/reports/{envelope['report_ref']}.json"])
    assert report["status"] == envelope["native_status"] == status
    restraint = next(
        f for f in report["findings"] if f["keepsake_id"] == "no-infallible-archive"
    )
    assert restraint["status"] == (
        "KEPT" if status == "DECLARED_RELEASE" else "NEEDS_REWORK"
    )
    assert restraint["missing_fields"] == (
        [] if status == "DECLARED_RELEASE" else ["drift_acknowledgment"]
    )
    assert any(f["status"] == "DECLARED_RELEASE" for f in report["findings"])


@pytest.mark.parametrize("present", [False, True])
def test_fixture_loader_allows_only_absent_or_null_release_as_absent(present):
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    if present:
        fixture["items"][0]["release"] = None
    assert fixture_items(fixture)[0].release is None
    envelope, _ = artifact_payloads(fixture)
    assert envelope["native_status"] == "KEPT"


def test_fixture_release_binds_subject_in_published_native_report():
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    release = ReleaseDeclaration(
        fixture["subject_id"],
        fixture["items"][0]["item_id"],
        "declared role",
        "2026-10-19",
        "synthetic:release-record",
    )
    fixture["items"][0]["release"] = asdict(release)
    assert fixture_items(fixture)[0].release == release
    envelope, _ = artifact_payloads(fixture)
    assert envelope["native_status"] == "DECLARED_RELEASE"
    fixture["subject_id"] = "another-subject"
    envelope, files = artifact_payloads(fixture)
    assert envelope["native_status"] == "NEEDS_REWORK"
    report = json.loads(files["data/reports/" + envelope["report_ref"] + ".json"])
    assert any(f["keepsake_id"] == "release-declaration" for f in report["findings"])


@pytest.mark.parametrize(
    "field", ["subject_id", "item_id", "declared_by", "declared_on", "source_ref"]
)
@pytest.mark.parametrize("value", [None, False, 0, "", " ", " padded ", [], {}])
def test_complete_malformed_release_remains_a_native_gap(field, value):
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    declaration = asdict(
        ReleaseDeclaration(
            fixture["subject_id"],
            fixture["items"][0]["item_id"],
            "declared role",
            "2026-10-19",
            "synthetic:release-record",
        )
    )
    declaration[field] = value
    fixture["items"][0]["release"] = declaration
    envelope, files = artifact_payloads(fixture)
    report = json.loads(files[f"data/reports/{envelope['report_ref']}.json"])
    assert report["status"] == envelope["native_status"] == "NEEDS_REWORK"
    assert any(
        f["keepsake_id"] == "release-declaration"
        and f["item_id"] == fixture["items"][0]["item_id"]
        and f["missing_fields"] == ["release"]
        for f in report["findings"]
    )
    assert not any(f["status"] == "DECLARED_RELEASE" for f in report["findings"])


@pytest.mark.parametrize(
    "subject, evidence, status",
    [
        ("subject-a", ["drift_acknowledgment"], "DECLARED_RELEASE"),
        ("subject-b", ["drift_acknowledgment"], "NEEDS_REWORK"),
        ("subject-a", [], "NEEDS_REWORK"),
    ],
)
def test_release_snapshot_replays_native_three_identity(subject, evidence, status):
    fixture = json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text()
    )
    fixture["subject_id"] = subject
    row = fixture["items"][0]
    row["custodian"] = ""
    row["evidence"] = evidence
    row["release"] = asdict(
        ReleaseDeclaration(
            "subject-a",
            row["item_id"],
            "declared role",
            "2026-10-19",
            "synthetic:release-record",
        )
    )
    envelope, files = artifact_payloads(fixture)
    report = json.loads(files[f"data/reports/{envelope['report_ref']}.json"])
    snapshot = json.loads(files[f"data/snapshots/{report['source_digest']}.json"])
    replay = read_succession(
        restore_source(snapshot),
        subject_id=subject,
        evaluated_as_of=fixture["review_date"],
    )
    assert (
        canonical_verdict(replay)
        == files[f"data/reports/{envelope['report_ref']}.json"]
    )
    assert report["schema_version"] == "silver.verdict/3.0"
    assert report["registry_version"] == "silver.registry/3.0"
    assert replay.status.value == envelope["native_status"] == status
    assert verdict_digest(replay) == envelope["report_ref"]
    restraint = next(
        f for f in replay.findings if f.keepsake_id == "no-infallible-archive"
    )
    assert restraint.status.value == ("KEPT" if evidence else "NEEDS_REWORK")


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
    assert verdict_digest(a) == verdict_digest(
        read_succession(item, evaluated_as_of="2026-10-20", subject_id="a")
    )
    assert (
        json.loads(canonical_verdict(read_succession(item)))["date_mode"] == "UNDATED"
    )
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
    verdict = read_succession(
        [item, None, replace(item, item_id="unknown", tags=frozenset({"unknown"}))]
    )
    assert verdict.status is VerdictStatus.KEPT
    assert (
        verdict.accepted_count,
        verdict.rejected_count,
        verdict.unmatched_count,
    ) == (2, 1, 1)
    assert verdict.reading_scope == "PARTIAL"
    gap = read_succession(replace(item, custodian=""))
    assert any(
        f.item_id == item.item_id and "custodian" in f.missing_fields
        for f in gap.findings
    )


def test_rejected_declaration_keeps_its_declared_id_and_blocks_duplicates():
    item = complete()
    broken = replace(item, description="")
    for items in ([item, broken], [broken, item]):
        verdict = read_succession(items)
        assert verdict.status is VerdictStatus.NEEDS_REWORK
        assert not verdict.findings
        assert (verdict.accepted_count, verdict.rejected_count) == (0, 2)
        assert all(n.item_id == item.item_id for n in verdict.intake_notes if n.item_id)
        assert any(
            n.item_id == item.item_id and "description" in n.note
            for n in verdict.intake_notes
        )


def test_conflicting_duplicate_declarations_have_order_independent_rejection():
    alpha = replace(complete(), item_id="duplicate", description="alpha")
    beta = replace(alpha, description="beta")
    verdicts = [
        read_succession(items)
        for items in ([alpha, beta], [beta, alpha], {alpha, beta})
    ]
    assert all(
        v.status is VerdictStatus.NEEDS_REWORK and not v.findings for v in verdicts
    )
    assert len({canonical_verdict(v) for v in verdicts}) == 1
    assert len({v.declaration_digest for v in verdicts}) == 1


def test_finite_container_boundary_and_normalization():
    assert read_succession(iter([complete()])).status is VerdictStatus.OUTSIDE_SCOPE
    assert read_succession(None).status is VerdictStatus.OUTSIDE_SCOPE
    for item in (
        replace(complete(), item_id=" bad "),
        replace(complete(), description=""),
    ):
        verdict = read_succession(item)
        assert verdict.rejected_count == 1
        assert any(n.item_id for n in verdict.intake_notes)
    verdict = read_succession(replace(complete(), tags=None, evidence=None))
    assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
    malformed = read_succession(
        replace(
            complete(), tags=frozenset({" Record ", None}), evidence=frozenset({42})
        )
    )
    assert malformed.intake_notes


def test_hash_seed_and_scan_permutations(tmp_path):
    program = "from silver_line import *; print(canonical_verdict(read_succession({SuccessionItem('a','x',frozenset({'record'})),SuccessionItem('b','y',frozenset({'artifact','unknown'}))})))"
    results = [
        subprocess.run(
            [sys.executable, "-c", program],
            env={**os.environ, "PYTHONHASHSEED": seed},
            check=True,
            text=True,
            capture_output=True,
        ).stdout
        for seed in ("1", "29", "104")
    ]
    assert len(set(results)) == 1


def test_legacy_digest_verification_keeps_original_schema():
    payload = canonical_verdict_v1(SuccessionVerdict(VerdictStatus.OUTSIDE_SCOPE))
    assert json.loads(payload)["schema_version"] == "1.0"
    assert "subject_id" not in json.loads(payload)
    assert sha256(payload.encode()).hexdigest() != verdict_digest(
        SuccessionVerdict(VerdictStatus.OUTSIDE_SCOPE)
    )


def test_every_envelope_field_has_a_negative_control():
    for path in sorted((ROOT / "data/fixtures").glob("*.json")):
        fixture = json.loads(path.read_text())
        envelope, files = artifact_payloads(fixture)
        verdict = read_succession(
            fixture_items(fixture),
            evaluated_as_of=fixture["review_date"],
            subject_id=fixture["subject_id"],
        )
        refs = tuple(envelope["source_snapshot_refs"])
        validate_envelope(envelope, verdict, refs)
        for key in envelope:
            broken = {**envelope, key: "mutated"}
            with pytest.raises(ValueError, match="envelope differs"):
                validate_envelope(broken, verdict, refs)
            with pytest.raises(ValueError):
                validate_envelope(
                    {k: v for k, v in envelope.items() if k != key}, verdict, refs
                )
        report = files["data/reports/" + envelope["report_ref"] + ".json"]
        assert sha256(report.encode()).hexdigest() == envelope["report_ref"]
        assert json.loads(report)["subject_id"] == fixture["subject_id"]
        payload = json.loads(report)
        from silver_line.registry import SILVER_KEEPSAKES
        from silver_line.serialization import registry_digest
        from silver_line.version import EVALUATOR_REVISION, REGISTRY_REVISION

        assert (
            payload["evaluated_as_of"]
            == envelope["review_date"]
            == fixture["review_date"]
        )
        assert (
            payload["registry_digest"]
            == envelope["registry_digest"]
            == registry_digest(SILVER_KEEPSAKES)
        )
        assert (
            payload["registry_version"]
            == envelope["registry_version"]
            == REGISTRY_REVISION
        )
        assert payload["evaluator_version"] == EVALUATOR_REVISION
        assert payload["schema_version"] == "silver.verdict/3.0"
        assert payload["status"] == envelope["native_status"]
        snapshot_hashes = {ref.split(":", 2)[1] for ref in refs}
        assert {
            payload["source_digest"],
            payload["declaration_digest"],
            payload["registry_digest"],
        } <= snapshot_hashes
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
    for verdict, refs in (
        (read_succession([]), ("ref",)),
        (
            read_succession([], (), evaluated_as_of="2026-10-20", subject_id="s"),
            ("ref",),
        ),
        (read_succession([], evaluated_as_of="2026-10-20", subject_id="s"), ()),
    ):
        with pytest.raises(ValueError):
            build_envelope(verdict, refs)
    valid = read_succession(complete(), evaluated_as_of="2026-10-20", subject_id="s")
    with pytest.raises(ValueError, match="immutable SHA-256"):
        build_envelope(valid, ("mutable:path",))
    with pytest.raises(ValueError, match="bind registry"):
        build_envelope(
            valid, ("sha256:" + "a" * 64 + ":data/snapshots/" + "a" * 64 + ".json",)
        )


def test_artifact_module_cli_checks_actual_store():
    subprocess.run(
        [sys.executable, "-m", "silver_line.artifacts", "--check"],
        check=True,
        capture_output=True,
        text=True,
    )


def test_empty_date_validation_is_explicit():
    assert validate_review_date("") == ""
