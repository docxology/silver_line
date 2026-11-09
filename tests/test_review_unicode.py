"""Consumer regressions for scalar-safe intake and rejected-source custody."""

from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path

import pytest

from silver_line import (
    ReleaseDeclaration,
    SuccessionItem,
    VerdictStatus,
    read_succession,
    read_succession_with_findings,
)
from silver_line.artifacts import (
    artifact_payloads,
    build_artifacts,
    fixture_items,
    validate_envelope,
)
from silver_line.serialization import canonical_verdict, verdict_digest

ROOT = Path(__file__).resolve().parents[1]
BAD_TEXT = ("\ud800", "\ud801", "\udc00", "\ud83d\ude00")
VALID_TEXT = ("ASCII", "caf\u00e9", "\U0001f600", "\ufffd", r"\ud800", r"\ud83d\ude00")
RELEASE_FIELDS = ("subject_id", "item_id", "declared_by", "declared_on", "source_ref")
BOUNDARIES = ("description", "item_id", "custodian", "tags", "evidence") + tuple(
    "release." + field for field in RELEASE_FIELDS
)


def fixture():
    return json.loads(
        (ROOT / "data/fixtures/silver_line_same_subject.json").read_text(
            encoding="utf-8"
        )
    )


def complete():
    return fixture_items(fixture())[0]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read(items):
    source = fixture()
    return read_succession(
        items, subject_id=source["subject_id"], evaluated_as_of=source["review_date"]
    )


def assert_native_utf8(verdict):
    text = canonical_verdict(verdict)
    assert sha256(text.encode("utf-8", errors="strict")).hexdigest() == verdict_digest(
        verdict
    )
    assert json.loads(text)["source_digest"] == verdict.source_digest
    for note in verdict.intake_notes:
        note.item_id.encode("utf-8", errors="strict")
        note.note.encode("utf-8", errors="strict")
    return text


def break_boundary(source, boundary, bad):
    row = source["items"][0]
    if boundary.startswith("release."):
        row["release"] = asdict(
            ReleaseDeclaration(
                source["subject_id"],
                row["item_id"],
                "declared role",
                "2026-10-19",
                "synthetic:release-record",
            )
        )
        row["release"][boundary.split(".")[1]] = bad
    elif boundary in ("tags", "evidence"):
        row[boundary].append(bad)
    else:
        row[boundary] = bad
    return source


def assert_artifact_custody(source):
    original_items = fixture_items(source)
    verdict = read_succession(
        original_items,
        subject_id=source["subject_id"],
        evaluated_as_of=source["review_date"],
    )
    envelope, files = artifact_payloads(source)
    report_text = files[f"data/reports/{envelope['report_ref']}.json"]
    assert report_text == assert_native_utf8(verdict)
    assert envelope["native_status"] == verdict.status.value
    refs = tuple(envelope["source_snapshot_refs"])
    validate_envelope(envelope, verdict, refs)
    canonical(envelope).encode("utf-8", errors="strict")
    for name, text in files.items():
        encoded = text.encode("utf-8", errors="strict")
        assert sha256(encoded).hexdigest() == Path(name).stem
        json.loads(encoded.decode("utf-8"))
    for ref in refs:
        scheme, digest, name = ref.split(":", 2)
        assert scheme == "sha256"
        assert sha256(files[name].encode("utf-8")).hexdigest() == digest
    assert {
        verdict.source_digest,
        verdict.declaration_digest,
        verdict.registry_digest,
    } <= {ref.split(":", 2)[1] for ref in refs}
    retained_source = json.loads(files[f"data/snapshots/{verdict.source_digest}.json"])
    source_replay = read_succession(
        fixture_items({"items": retained_source}),
        subject_id=source["subject_id"],
        evaluated_as_of=source["review_date"],
    )
    assert canonical_verdict(source_replay) == report_text
    assert verdict_digest(source_replay) == envelope["report_ref"]

    # Replay the retained ORIGINAL fixture, never the accepted-only array.
    retained = [
        json.loads(text)
        for name, text in files.items()
        if name.startswith("data/snapshots/")
        and isinstance(json.loads(text), dict)
        and set(json.loads(text)) == set(source)
    ]
    assert len(retained) == 1
    restored_items = fixture_items(retained[0])
    assert restored_items == original_items
    replay = read_succession(
        restored_items,
        subject_id=retained[0]["subject_id"],
        evaluated_as_of=retained[0]["review_date"],
    )
    assert canonical_verdict(replay) == report_text
    assert verdict_digest(replay) == envelope["report_ref"]
    assert artifact_payloads(retained[0]) == (envelope, files)
    return verdict, envelope, files


@pytest.mark.parametrize("api", [read_succession, read_succession_with_findings])
@pytest.mark.parametrize("bad", BAD_TEXT)
def test_malformed_description_is_rejected_before_original_source_hashing(api, bad):
    item = SuccessionItem(bad)
    result = api(item, evaluated_as_of="2026-10-20")
    verdict = result[0] if isinstance(result, tuple) else result
    if isinstance(result, tuple):
        assert result[1] == verdict.findings
    assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
    assert not verdict.findings
    assert (
        verdict.accepted_count,
        verdict.rejected_count,
        verdict.unmatched_count,
    ) == (0, 1, 0)
    assert verdict.reading_scope == "PARTIAL"
    description_notes = [n for n in verdict.intake_notes if "description" in n.note]
    assert description_notes
    assert all(n.disposition.value == "SET_ASIDE" for n in description_notes)
    assert all(n.item_id.startswith("input-") for n in description_notes)
    assert all(len(n.item_id) == len("input-") + 64 for n in description_notes)
    assert_native_utf8(verdict)
    again = api(item, evaluated_as_of="2026-10-20")
    assert canonical_verdict(again[0] if isinstance(again, tuple) else again) == (
        canonical_verdict(verdict)
    )


def test_rejected_code_units_have_distinct_source_and_fallback_identities():
    verdicts = [read(SuccessionItem(text)) for text in BAD_TEXT]
    assert len({v.source_digest for v in verdicts}) == len(BAD_TEXT)
    assert len({verdict_digest(v) for v in verdicts}) == len(BAD_TEXT)
    controls = [read(SuccessionItem(text)) for text in VALID_TEXT]
    assert len({v.source_digest for v in verdicts + controls}) == (
        len(BAD_TEXT) + len(VALID_TEXT)
    )
    ids = [
        next(n.item_id for n in v.intake_notes if "description" in n.note)
        for v in verdicts
    ]
    assert len(set(ids)) == len(BAD_TEXT)
    assert len({v.declaration_digest for v in verdicts}) == 1
    assert all(not v.findings and v.rejected_count == 1 for v in verdicts)
    for verdict in verdicts:
        assert_native_utf8(verdict)


@pytest.mark.parametrize("bad", BAD_TEXT)
def test_rejected_unicode_counts_declarations_not_notes_and_preserves_good_findings(
    bad,
):
    good = complete()
    rejected = replace(good, item_id="rejected-description", description=bad)
    invalid_id = replace(good, item_id=bad)
    scans = ([good, rejected, invalid_id, None], [None, invalid_id, rejected, good])
    verdicts = [read(scan) for scan in scans]
    for verdict in verdicts:
        assert verdict.status is VerdictStatus.KEPT
        assert verdict.reading_scope == "PARTIAL"
        assert (
            verdict.accepted_count,
            verdict.rejected_count,
            verdict.unmatched_count,
        ) == (1, 3, 0)
        assert verdict.findings == read(good).findings
        assert any(
            n.item_id == "rejected-description" and n.disposition.value == "SET_ASIDE"
            for n in verdict.intake_notes
        )
        assert any(n.item_id.startswith("input-") for n in verdict.intake_notes)
        assert_native_utf8(verdict)
    assert canonical_verdict(verdicts[0]) == canonical_verdict(verdicts[1])


@pytest.mark.parametrize("bad", BAD_TEXT)
def test_valid_duplicate_id_still_rejects_whole_finite_scan_with_bad_description(bad):
    good = complete()
    broken = replace(good, description=bad)
    verdicts = [
        read(scan)
        for scan in (
            [good, broken],
            [broken, good],
            {good, broken},
            frozenset({good, broken}),
        )
    ]
    for verdict in verdicts:
        assert verdict.status is VerdictStatus.NEEDS_REWORK
        assert not verdict.findings
        assert verdict.reading_scope == "PARTIAL"
        assert (
            verdict.accepted_count,
            verdict.rejected_count,
            verdict.unmatched_count,
        ) == (0, 2, 0)
        assert all(n.item_id == good.item_id for n in verdict.intake_notes if n.item_id)
        assert any("duplicate item_id" in n.note for n in verdict.intake_notes)
        assert any("description" in n.note for n in verdict.intake_notes)
        assert_native_utf8(verdict)
    assert len({canonical_verdict(v) for v in verdicts}) == 1
    assert len({verdict_digest(v) for v in verdicts}) == 1


@pytest.mark.parametrize("boundary", BOUNDARIES)
@pytest.mark.parametrize("bad", BAD_TEXT)
def test_each_declared_text_boundary_has_safe_complete_artifact_replay(boundary, bad):
    source = break_boundary(fixture(), boundary, bad)
    verdict, envelope, files = assert_artifact_custody(source)
    normalized = json.loads(files[f"data/snapshots/{verdict.declaration_digest}.json"])
    if boundary in ("description", "item_id"):
        assert verdict.status is VerdictStatus.OUTSIDE_SCOPE
        assert (verdict.accepted_count, verdict.rejected_count) == (0, 1)
        assert verdict.reading_scope == "PARTIAL"
        assert normalized == []
        assert not verdict.findings
        assert any(n.disposition.value == "SET_ASIDE" for n in verdict.intake_notes)
    else:
        assert (
            verdict.accepted_count,
            verdict.rejected_count,
            verdict.unmatched_count,
        ) == (1, 0, 0)
        assert verdict.reading_scope == "COMPLETE"
        if boundary == "custodian":
            assert verdict.status is VerdictStatus.NEEDS_REWORK
            assert normalized[0]["custodian"] == ""
            assert any("custodian" in f.missing_fields for f in verdict.findings)
        elif boundary in ("tags", "evidence"):
            assert verdict.status is VerdictStatus.KEPT
            assert normalized[0][boundary] == sorted(
                set(fixture()["items"][0][boundary])
            )
            assert any(n.disposition.value == "SET_ASIDE" for n in verdict.intake_notes)
        else:
            assert verdict.status is VerdictStatus.NEEDS_REWORK
            assert any(
                f.keepsake_id == "release-declaration"
                and f.missing_fields == ("release",)
                for f in verdict.findings
            )
            assert not any(
                f.status.value == "DECLARED_RELEASE" for f in verdict.findings
            )
    assert any(
        f"accepted={verdict.accepted_count}; rejected={verdict.rejected_count}; "
        f"unmatched={verdict.unmatched_count}" in note
        for note in envelope["scope_and_nonclaims"]
    )


@pytest.mark.parametrize("bad", BAD_TEXT)
def test_malformed_labels_cannot_supply_missing_tag_or_evidence(bad):
    good = complete()
    tagless = read(replace(good, tags=frozenset({bad})))
    assert tagless.status is VerdictStatus.OUTSIDE_SCOPE
    assert not tagless.findings
    assert (
        tagless.accepted_count,
        tagless.rejected_count,
        tagless.unmatched_count,
    ) == (1, 0, 1)
    assert tagless.reading_scope == "PARTIAL"
    missing = read(
        replace(good, evidence=(good.evidence - {"custodian_acknowledgment"}) | {bad})
    )
    assert missing.status is VerdictStatus.NEEDS_REWORK
    assert any("custodian_acknowledgment" in f.missing_fields for f in missing.findings)
    assert (missing.accepted_count, missing.rejected_count) == (1, 0)
    for verdict in (tagless, missing):
        assert any(n.disposition.value == "SET_ASIDE" for n in verdict.intake_notes)
        assert_native_utf8(verdict)


def test_valid_unicode_bytes_and_literal_escapes_remain_distinct():
    identities = []
    for text in VALID_TEXT:
        source = fixture()
        row = source["items"][0]
        row["description"] = text
        row["custodian"] = "successor " + text
        row["item_id"] = "item-" + text
        expected_row = {
            **row,
            "tags": sorted(row["tags"]),
            "evidence": sorted(row["evidence"]),
            "release": None,
        }
        expected_source = canonical([expected_row]).encode("utf-8")
        expected_fixture = canonical(source).encode("utf-8")
        verdict, _, files = assert_artifact_custody(source)
        assert verdict.status is VerdictStatus.KEPT
        assert (verdict.accepted_count, verdict.rejected_count) == (1, 0)
        assert not verdict.intake_notes
        assert verdict.source_digest == sha256(expected_source).hexdigest()
        assert verdict.declaration_digest == verdict.source_digest
        assert files[f"data/snapshots/{verdict.source_digest}.json"].encode(
            "utf-8"
        ) == (expected_source)
        assert (
            files[f"data/snapshots/{sha256(expected_fixture).hexdigest()}.json"].encode(
                "utf-8"
            )
            == expected_fixture
        )
        identities.append(verdict.source_digest)
    malformed = [
        read(replace(complete(), description=text)).source_digest for text in BAD_TEXT
    ]
    assert len(set(identities + malformed)) == len(VALID_TEXT) + len(BAD_TEXT)


def test_rejected_source_store_writes_utf8_and_replays_without_losing_rejections(
    tmp_path,
):
    source = fixture()
    good = dict(source["items"][0])
    source["items"].extend(
        [
            {**good, "item_id": "rejected-one", "description": BAD_TEXT[0]},
            {**good, "item_id": "rejected-two", "description": BAD_TEXT[1]},
            {**good, "item_id": BAD_TEXT[2]},
        ]
    )
    verdict, envelope, files = assert_artifact_custody(source)
    assert verdict.status is VerdictStatus.KEPT
    assert (
        verdict.accepted_count,
        verdict.rejected_count,
        verdict.unmatched_count,
    ) == (1, 3, 0)
    assert verdict.reading_scope == "PARTIAL"
    accepted = json.loads(files[f"data/snapshots/{verdict.declaration_digest}.json"])
    accepted_only = read(fixture_items({"items": accepted}))
    assert accepted_only.rejected_count == 0
    assert accepted_only.source_digest != verdict.source_digest
    assert canonical_verdict(accepted_only) != canonical_verdict(verdict)

    fixture_dir = tmp_path / "data/fixtures"
    fixture_dir.mkdir(parents=True)
    # ASCII JSON escapes are legal UTF-8 fixture bytes; decoding exposes bad text.
    (fixture_dir / "unicode.json").write_text(
        json.dumps(source, ensure_ascii=True), encoding="utf-8"
    )
    outputs = build_artifacts(tmp_path)
    assert outputs == build_artifacts(tmp_path, check=True)
    assert outputs == build_artifacts(tmp_path)
    for name in outputs:
        text = (tmp_path / name).read_bytes().decode("utf-8", errors="strict")
        if name in files:
            assert text == files[name]
        else:
            assert name == "data/envelopes/unicode.json"
            assert json.loads(text) == envelope


@pytest.mark.parametrize(
    "name", ["silver_line_same_subject.json", "silver_line_worked.json"]
)
def test_existing_fixture_and_source_snapshot_bytes_remain_unchanged(name):
    source = json.loads((ROOT / "data/fixtures" / name).read_text(encoding="utf-8"))
    rows = [
        {
            **row,
            "tags": sorted(row["tags"]),
            "evidence": sorted(row["evidence"]),
            "release": None,
        }
        for row in source["items"]
    ]
    expected_source = canonical(sorted(rows, key=canonical)).encode("utf-8")
    expected_fixture = canonical(source).encode("utf-8")
    verdict, _, files = assert_artifact_custody(source)
    assert verdict.source_digest == sha256(expected_source).hexdigest()
    for expected in (expected_source, expected_fixture):
        path = f"data/snapshots/{sha256(expected).hexdigest()}.json"
        assert files[path].encode("utf-8") == expected
        assert (ROOT / path).read_bytes() == expected
