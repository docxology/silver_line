"""Fail-closed staged intake for succession declarations.

Intake runs before any scoring. Malformed input (non-string labels, blank
descriptions, untrusted tag vocabulary) is set aside with an intake note
rather than crashing or being silently repaired into a fabricated value.
An empty scan set fails closed: a reading with nothing declared is
``OUTSIDE_SCOPE`` with a note, never a favourable default.
"""

from __future__ import annotations

from collections.abc import Iterable

from .enums import IntakeDisposition
from .records import IntakeNote, SuccessionItem
from .registry import KEEPSAKE_TAG_VOCABULARY


def normalize_item(raw: object) -> tuple[SuccessionItem | None, list[IntakeNote]]:
    """Normalize one incoming succession declaration.

    Returns the usable record (or ``None`` when the item is unusable) and the
    intake notes describing every set-aside or repair. The function never
    raises on malformed content: malformed content is an outcome, recorded.
    """

    notes: list[IntakeNote] = []
    if not isinstance(raw, SuccessionItem):
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "declaration is not a SuccessionItem record and was set aside",
            )
        )
        return None, notes
    if not isinstance(raw.description, str) or not raw.description.strip():
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "description is empty or not text; the item cannot be scored",
            )
        )
        return None, notes
    if not isinstance(raw.custodian, str):
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "custodian is not text and was dropped; restate the custodian",
            )
        )
        raw = SuccessionItem(
            description=raw.description,
            custodian="",
            tags=raw.tags if isinstance(raw.tags, frozenset) else frozenset(),
            evidence=(
                raw.evidence if isinstance(raw.evidence, frozenset) else frozenset()
            ),
        )
    elif not raw.custodian.strip():
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "custodian is blank; the item is scored but entrustment gaps will surface",
            )
        )
    if not isinstance(raw.tags, frozenset) or not isinstance(raw.evidence, frozenset):
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "tags or evidence is not a frozen label set and was dropped",
            )
        )
        raw = SuccessionItem(
            description=raw.description,
            custodian=raw.custodian if isinstance(raw.custodian, str) else "",
            tags=raw.tags if isinstance(raw.tags, frozenset) else frozenset(),
            evidence=(
                raw.evidence if isinstance(raw.evidence, frozenset) else frozenset()
            ),
        )
    return raw, notes


def clean_labels(raw: object, field_name: str) -> tuple[frozenset[str], list[IntakeNote]]:
    """Normalize a declared label collection without letting bad input crash.

    Returns the kept labels (stripped, lowercased) and intake notes for every
    declaration or token that had to be ignored.
    """

    if isinstance(raw, str) or not isinstance(raw, Iterable):
        return frozenset(), [
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                f"{field_name} declaration is not a collection of labels and was ignored",
            )
        ]
    kept: set[str] = set()
    notes: list[IntakeNote] = []
    for token in raw:
        if not isinstance(token, str) or not token.strip():
            notes.append(
                IntakeNote(
                    IntakeDisposition.SET_ASIDE,
                    f"ignored a malformed {field_name} label",
                )
            )
            continue
        kept.add(token.strip().lower())
    return frozenset(kept), notes


def vocabulary_check(
    tags: frozenset[str],
) -> list[IntakeNote]:
    """Flag declared tags outside the reviewed vocabulary; nothing is deleted.

    Out-of-vocabulary tags are set aside from matching (they would make the
    reading unreviewable) but recorded so the declarer can fix or propose them.
    """

    return [
        IntakeNote(
            IntakeDisposition.SET_ASIDE,
            f"tag '{tag}' is outside the reviewed vocabulary and did not match",
        )
        for tag in sorted(tags - KEEPSAKE_TAG_VOCABULARY)
    ]


def intake(raw_items: object) -> tuple[tuple[SuccessionItem, ...], tuple[IntakeNote, ...]]:
    """Stage a scan set of succession declarations.

    Fail closed: an empty scan set returns no items with an explicit note, so
    downstream evaluation reports ``OUTSIDE_SCOPE`` rather than a default
    verdict. Unknown or malformed members are set aside with notes.
    """

    if raw_items is None:
        return (), (
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "scan set is absent; nothing was declared for reading",
            ),
        )
    if isinstance(raw_items, SuccessionItem):
        raw_items = (raw_items,)
    if isinstance(raw_items, str) or not isinstance(raw_items, Iterable):
        return (), (
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "scan set is not a collection of declarations and was ignored",
            ),
        )
    items: list[SuccessionItem] = []
    notes: list[IntakeNote] = []
    for raw in raw_items:
        item, item_notes = normalize_item(raw)
        notes.extend(item_notes)
        if item is not None:
            items.append(item)
    if not items:
        notes.append(
            IntakeNote(
                IntakeDisposition.SET_ASIDE,
                "scan set contained no usable declarations; the reading fails closed",
            )
        )
    return tuple(items), tuple(notes)
