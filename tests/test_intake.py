"""Staged intake: malformed input is set aside with notes, never invented."""

from __future__ import annotations

from silver_line.enums import IntakeDisposition
from silver_line.intake import clean_labels, intake, normalize_item
from silver_line.records import SuccessionItem


def test_empty_scan_set_fails_closed_with_note() -> None:
    items, notes = intake([])
    assert items == ()
    assert notes
    assert all(note.disposition is IntakeDisposition.SET_ASIDE for note in notes)


def test_absent_scan_set_fails_closed_with_note() -> None:
    items, notes = intake(None)
    assert items == ()
    assert notes


def test_non_collection_scan_set_is_set_aside() -> None:
    items, notes = intake(42)
    assert items == ()
    assert notes


def test_malformed_member_is_set_aside_not_crash() -> None:
    items, notes = intake(["not a record", None, 123])
    assert items == ()
    assert len(notes) >= 3


def test_blank_description_is_set_aside() -> None:
    items, notes = intake([SuccessionItem(description="   ")])
    assert items == ()
    assert any("description" in note.note for note in notes)


def test_valid_item_is_accepted() -> None:
    item = SuccessionItem(description="lab notebooks", custodian="M. Lennon",
                          tags=frozenset({"record"}), evidence=frozenset({"handoff_note"}))
    items, notes = intake(item)
    assert items == (item,)
    assert not notes


def test_clean_labels_normalizes_and_notes_malformed() -> None:
    kept, notes = clean_labels(["  Record ", "", 7, None], "tag")
    assert kept == frozenset({"record"})
    assert len(notes) == 3


def test_clean_labels_rejects_non_collection() -> None:
    kept, notes = clean_labels("record", "tag")
    assert kept == frozenset()
    assert notes


def test_normalize_item_drops_non_text_custodian() -> None:
    raw = SuccessionItem(description="x", custodian=None)  # type: ignore[arg-type]
    item, notes = normalize_item(raw)
    assert item is not None
    assert item.custodian == ""
    assert notes
