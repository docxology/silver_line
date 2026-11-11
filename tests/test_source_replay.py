"""Native source custody regressions; fixture admission is a separate boundary."""

from dataclasses import replace
import json

import pytest

from silver_line import (
    ReleaseDeclaration,
    SOURCE_CODEC,
    SuccessionItem,
    VerdictStatus,
    canonical_source,
    canonical_verdict,
    read_succession,
    restore_source,
    verdict_digest,
)
from silver_line.artifacts import artifact_payloads, fixture_items


SUBJECT = "synthetic:source-replay"
DATE = "2026-10-20"


def released_item():
    return SuccessionItem(
        "declared record",
        "declared custodian",
        frozenset({"record"}),
        frozenset({"drift_acknowledgment"}),
        "record-one",
        ReleaseDeclaration(
            SUBJECT, "record-one", "declared role", DATE, "synthetic:release"
        ),
    )


def read(raw):
    return read_succession(raw, subject_id=SUBJECT, evaluated_as_of=DATE)


def replay(raw):
    encoded = canonical_source(raw)
    encoded.encode("utf-8", errors="strict")
    restored = restore_source(json.loads(encoded))
    assert canonical_source(restored) == encoded
    before, after = read(raw), read(restored)
    assert canonical_verdict(after) == canonical_verdict(before)
    assert verdict_digest(after) == verdict_digest(before)
    return restored, after


@pytest.mark.parametrize("field", ["tags", "evidence"])
@pytest.mark.parametrize("container", [list, tuple, set, frozenset])
def test_native_label_container_custody_cannot_grant_release(field, container):
    valid = released_item()
    assert read(valid).status is VerdictStatus.DECLARED_RELEASE
    raw = replace(valid, **{field: container(getattr(valid, field))})
    restored, verdict = replay((raw,))
    assert type(getattr(restored[0], field)) is container
    if container is frozenset:
        assert verdict.status is VerdictStatus.DECLARED_RELEASE
    else:
        assert verdict.status is VerdictStatus.NEEDS_REWORK
        if field == "tags":
            assert not any(
                f.status.value == "DECLARED_RELEASE" for f in verdict.findings
            )
        else:
            restraint = next(
                f for f in verdict.findings if f.keepsake_id == "no-infallible-archive"
            )
            assert restraint.status.value == "NEEDS_REWORK"
        assert verdict.intake_notes
        assert verdict.source_digest != read((valid,)).source_digest


@pytest.mark.parametrize("container", [list, tuple, set, frozenset])
def test_root_scan_syntax_keeps_order_insensitive_report_identity(container):
    item = released_item()
    restored, verdict = replay(container([item]))
    assert type(restored) is tuple
    assert restored == (item,)
    assert canonical_verdict(verdict) == canonical_verdict(read(item))


@pytest.mark.parametrize(
    "field", ["subject_id", "item_id", "declared_by", "declared_on", "source_ref"]
)
@pytest.mark.parametrize(
    "value",
    [
        {},
        {"record": "different"},
        {"record": ["second", "first", {"nested": (None, False, 1.5)}]},
        {"silver_line.text-code-units/1": [55296]},
        {"kind": "text-code-units", "value": [55296]},
        {"codec": SOURCE_CODEC, "value": {"kind": "unsupported", "value": "os.system"}},
        {"\ud800": {"nested": "\ud83d\ude00"}},
    ],
)
def test_nested_malformed_release_values_are_lossless_and_never_release(field, value):
    item = released_item()
    raw = replace(item, release=replace(item.release, **{field: value}))
    restored, verdict = replay((raw,))
    assert getattr(restored[0].release, field) == value
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert any(f.keepsake_id == "release-declaration" for f in verdict.findings)
    assert not any(f.status.value == "DECLARED_RELEASE" for f in verdict.findings)


def test_distinct_malformed_dictionary_values_have_distinct_report_identities():
    values = ({}, {"record": "first"}, {"record": "second"})
    verdicts = []
    for value in values:
        item = released_item()
        _, verdict = replay(
            (replace(item, release=replace(item.release, source_ref=value)),)
        )
        verdicts.append(verdict)
    assert len({v.source_digest for v in verdicts}) == len(values)
    assert len({v.declaration_digest for v in verdicts}) == len(values)
    assert len({verdict_digest(v) for v in verdicts}) == len(values)
    assert all(v.status is VerdictStatus.NEEDS_REWORK for v in verdicts)


@pytest.mark.parametrize("container", [list, tuple])
def test_ordered_nested_values_survive_order_insensitive_root_scan(container):
    item = released_item()
    alpha = replace(
        item, release=replace(item.release, source_ref=container(["b", "a"]))
    )
    beta = replace(item, item_id="other")
    restored, forward = replay(container([alpha, beta]))
    retained_alpha = next(i for i in restored if i.item_id == alpha.item_id)
    assert type(retained_alpha.release.source_ref) is container
    assert retained_alpha.release.source_ref == container(["b", "a"])
    _, reverse = replay(container([beta, alpha]))
    assert canonical_verdict(forward) == canonical_verdict(reverse)
    changed = replace(
        alpha, release=replace(alpha.release, source_ref=container(["a", "b"]))
    )
    assert read((alpha,)).source_digest != read((changed,)).source_digest


def test_fixture_admission_does_not_interpret_native_or_historical_markers():
    value = {"silver_line.text-code-units/1": [55296]}
    row = {
        "description": "record",
        "custodian": "custodian",
        "tags": ["record"],
        "evidence": ["drift_acknowledgment"],
        "item_id": "record-one",
        "release": {
            "subject_id": SUBJECT,
            "item_id": "record-one",
            "declared_by": "role",
            "declared_on": DATE,
            "source_ref": value,
        },
    }
    fixture = {"subject_id": SUBJECT, "review_date": DATE, "items": [row]}
    admitted = fixture_items(fixture)
    assert admitted[0].release.source_ref == value
    assert admitted[0].tags == frozenset({"record"})
    envelope, files = artifact_payloads(fixture)
    verdict = read(admitted)
    restored = restore_source(
        json.loads(files[f"data/snapshots/{verdict.source_digest}.json"])
    )
    assert restored == admitted
    assert (
        canonical_verdict(read(restored))
        == files[f"data/reports/{envelope['report_ref']}.json"]
    )
    original = restore_source(json.loads(canonical_source(fixture)))
    assert original == fixture
    assert artifact_payloads(original) == (envelope, files)


@pytest.mark.parametrize("bad_id", [None, 42, " spaced ", "\ud800"])
def test_repeated_invalid_ids_do_not_suppress_a_usable_declaration(bad_id):
    good = released_item()
    invalid = replace(good, item_id=bad_id)
    restored, verdict = replay([good, invalid, invalid])
    assert restored[1].item_id == bad_id
    assert verdict.status is VerdictStatus.DECLARED_RELEASE
    assert verdict.findings == read([good]).findings
    assert (verdict.accepted_count, verdict.rejected_count) == (1, 2)
    assert verdict.reading_scope == "PARTIAL"
    assert not any("duplicate item_id" in n.note for n in verdict.intake_notes)


def test_declared_input_prefix_does_not_collide_with_diagnostic_identity():
    invalid = replace(released_item(), item_id=None)
    diagnostic = next(n.item_id for n in read([invalid]).intake_notes if n.item_id)
    good = replace(released_item(), item_id=diagnostic, release=None)
    _, verdict = replay([invalid, good])
    assert verdict.findings == read([good]).findings
    assert (verdict.accepted_count, verdict.rejected_count) == (1, 1)
    assert not any("duplicate item_id" in n.note for n in verdict.intake_notes)


def test_canonical_declared_duplicates_still_reject_unusable_descriptions():
    good = released_item()
    broken = replace(good, description="\ud800")
    _, verdict = replay([good, broken])
    assert verdict.status is VerdictStatus.NEEDS_REWORK
    assert not verdict.findings
    assert (verdict.accepted_count, verdict.rejected_count) == (0, 2)
    assert any(
        "duplicate item_id" in n.note and n.item_id == good.item_id
        for n in verdict.intake_notes
    )


def test_omitted_id_keeps_content_derived_identity_on_replay():
    raw = replace(released_item(), item_id="", release=None)
    _, verdict = replay(raw)
    assert verdict.accepted_count == 1
    assert all(f.item_id.startswith("input-") for f in verdict.findings)


@pytest.mark.parametrize(
    "snapshot",
    [
        [],
        {"items": []},
        {"codec": "silver.source/0", "value": None},
        {"codec": SOURCE_CODEC, "value": {"kind": "os.system", "value": "bad"}},
        {"codec": SOURCE_CODEC, "value": {"kind": "SuccessionItem", "value": {}}},
        {
            "codec": SOURCE_CODEC,
            "value": {"kind": "text-code-units", "value": [True, 55296]},
        },
        {"codec": SOURCE_CODEC, "value": {"kind": "text-code-units", "value": [65]}},
        {
            "codec": SOURCE_CODEC,
            "value": {"kind": "text-code-units", "value": [1114112, 55296]},
        },
        {
            "codec": SOURCE_CODEC,
            "value": {"kind": "dict", "value": [["x", 1], ["x", 2]]},
        },
        {"codec": SOURCE_CODEC, "value": {"kind": "set", "value": [1, 1]}},
        {"codec": SOURCE_CODEC, "value": {"kind": "scan", "value": None}},
        {"codec": SOURCE_CODEC, "value": {"kind": "text-code-units", "value": []}},
        {
            "codec": SOURCE_CODEC,
            "value": {"kind": "set", "value": [{"kind": "list", "value": []}]},
        },
        {
            "codec": SOURCE_CODEC,
            "value": {
                "kind": "dict",
                "value": [[{"kind": "list", "value": []}, 1]],
            },
        },
    ],
)
def test_source_decoder_refuses_historical_unknown_or_malformed_snapshots(snapshot):
    with pytest.raises(ValueError):
        restore_source(snapshot)


def test_unsupported_producer_has_no_arbitrary_object_loading_path():
    snapshot = json.loads(canonical_source(object()))
    with pytest.raises(ValueError, match="unsupported"):
        restore_source(snapshot)
