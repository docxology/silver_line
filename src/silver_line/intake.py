from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from .enums import IntakeDisposition
from .records import IntakeNote, SuccessionItem
from .registry import KEEPSAKE_TAG_VOCABULARY


def normalize_item(raw: object) -> tuple[SuccessionItem | None, list[IntakeNote]]:
    notes: list[IntakeNote] = []
    if not isinstance(raw, SuccessionItem):
        return None, [IntakeNote(IntakeDisposition.SET_ASIDE,
                                "declaration is not a SuccessionItem record and was set aside")]
    item_id = raw.item_id if isinstance(raw.item_id, str) else ""
    if not isinstance(raw.description, str) or not raw.description.strip():
        return None, [IntakeNote(IntakeDisposition.SET_ASIDE,
                                "description is empty or not text; the item cannot be scored", item_id)]
    if not isinstance(raw.item_id, str) or raw.item_id != raw.item_id.strip():
        return None, [IntakeNote(IntakeDisposition.SET_ASIDE,
                                "item_id must be canonical text; item was set aside", item_id)]
    if not isinstance(raw.custodian, str) or not raw.custodian.strip():
        notes.append(IntakeNote(IntakeDisposition.SET_ASIDE,
                                "custodian is blank or not text; entrustment gaps will surface", item_id))
    tags = raw.tags if isinstance(raw.tags, frozenset) else frozenset()
    evidence = raw.evidence if isinstance(raw.evidence, frozenset) else frozenset()
    if tags is not raw.tags or evidence is not raw.evidence:
        notes.append(IntakeNote(IntakeDisposition.SET_ASIDE,
                                "tags or evidence is not a frozen label set and was dropped", item_id))
    return replace(raw, description=raw.description.strip(),
                   custodian=raw.custodian.strip() if isinstance(raw.custodian, str) else "",
                   tags=tags, evidence=evidence), notes


def clean_labels(raw: object, field_name: str) -> tuple[frozenset[str], list[IntakeNote]]:
    if isinstance(raw, str) or not isinstance(raw, Iterable):
        return frozenset(), [IntakeNote(IntakeDisposition.SET_ASIDE,
                                       f"{field_name} declaration is not a collection of labels and was ignored")]
    kept: set[str] = set()
    notes: list[IntakeNote] = []
    for token in raw:
        if not isinstance(token, str) or not token.strip():
            notes.append(IntakeNote(IntakeDisposition.SET_ASIDE,
                                    f"ignored a malformed {field_name} label"))
        else:
            kept.add(token.strip().lower())
    return frozenset(kept), notes


def vocabulary_check(tags: frozenset[str]) -> list[IntakeNote]:
    return [IntakeNote(IntakeDisposition.SET_ASIDE,
                       f"tag '{tag}' is outside the reviewed vocabulary and did not match")
            for tag in sorted(tags - KEEPSAKE_TAG_VOCABULARY)]


def intake(raw_items: object) -> tuple[tuple[SuccessionItem, ...], tuple[IntakeNote, ...]]:
    if raw_items is None:
        return (), (IntakeNote(IntakeDisposition.SET_ASIDE,
                               "scan set is absent; nothing was declared for reading"),)
    if isinstance(raw_items, SuccessionItem):
        raw_items = (raw_items,)
    if not isinstance(raw_items, (list, tuple, set, frozenset)):
        return (), (IntakeNote(IntakeDisposition.SET_ASIDE,
                               "scan set must be a finite list, tuple, set or frozenset of declarations"),)
    items: list[SuccessionItem] = []
    notes: list[IntakeNote] = []
    for raw in raw_items:
        item, item_notes = normalize_item(raw)
        notes.extend(item_notes)
        if item is not None:
            items.append(item)
    if not items:
        notes.append(IntakeNote(IntakeDisposition.SET_ASIDE,
                                "scan set contained no usable declarations; the reading fails closed"))
    return tuple(items), tuple(sorted(notes, key=lambda n: (n.item_id, n.disposition.value, n.note)))
