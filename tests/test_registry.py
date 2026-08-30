"""The keepsake registry: shape, balance, and vocabulary."""

from __future__ import annotations

from silver_line.enums import KeepKind
from silver_line.registry import KEEPSAKE_TAG_VOCABULARY, SILVER_KEEPSAKES, registry_ids
from silver_line.serialization import canonical_registry, registry_digest


def test_registry_has_at_least_six_entries() -> None:
    assert len(SILVER_KEEPSAKES) >= 6


def test_registry_ids_are_unique_and_sorted_emit_matches() -> None:
    ids = registry_ids()
    assert len(ids) == len(set(ids))
    assert sorted(ids) == sorted(registry_ids())


def test_every_keepsake_has_required_evidence() -> None:
    for keepsake in SILVER_KEEPSAKES:
        assert keepsake.required_evidence
        assert all(label.strip() for label in keepsake.required_evidence)


def test_all_keep_kinds_represented() -> None:
    used = {keepsake.kind for keepsake in SILVER_KEEPSAKES}
    assert used == set(KeepKind)


def test_tags_within_vocabulary() -> None:
    for keepsake in SILVER_KEEPSAKES:
        assert keepsake.tags <= KEEPSAKE_TAG_VOCABULARY


def test_registry_digest_is_stable() -> None:
    assert registry_digest(SILVER_KEEPSAKES) == registry_digest(SILVER_KEEPSAKES)
    assert len(registry_digest(SILVER_KEEPSAKES)) == 64


def test_canonical_registry_sorts_entries() -> None:
    text = canonical_registry(SILVER_KEEPSAKES)
    assert text == canonical_registry(tuple(reversed(SILVER_KEEPSAKES)))


def test_may_lapse_keepsakes_exist() -> None:
    lapse_named = [keepsake for keepsake in SILVER_KEEPSAKES if keepsake.may_lapse]
    assert lapse_named, "the set must name what is allowed to lapse"
