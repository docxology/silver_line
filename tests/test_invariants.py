"""The invariant battery over the Silver declaration and negative controls."""

from __future__ import annotations

from silver_line.enums import KeepKind
from silver_line.invariants import all_invariants, check_unique_keepsake_ids
from silver_line.records import Keepsake
from silver_line.registry import SILVER_KEEPSAKES


def test_all_invariants_pass_on_the_declaration() -> None:
    results = all_invariants(SILVER_KEEPSAKES)
    assert results
    for result in results:
        assert result.passed, (result.name, result.reasons)


def test_empty_registry_fails_nonempty_check() -> None:
    results = all_invariants(())
    failed = {r.name for r in results if not r.passed}
    assert "nonempty_registry" in failed


def test_duplicate_ids_fail() -> None:
    keepsake = SILVER_KEEPSAKES[0]
    result = check_unique_keepsake_ids((keepsake, keepsake))
    assert not result.passed


def test_unknown_tag_fails_vocabulary_check() -> None:
    bad = (Keepsake("x", "t", "w", frozenset({"zzz"}), ("a",)),)
    results = all_invariants(bad)
    failed = {r.name for r in results if not r.passed}
    assert "tags_in_vocabulary" in failed


def test_lapse_family_missing_fails() -> None:
    retention_only = tuple(
        keepsake for keepsake in SILVER_KEEPSAKES if keepsake.kind is not KeepKind.LAPSE
    )
    results = all_invariants(retention_only)
    failed = {r.name for r in results if not r.passed}
    assert "lapse_families_present" in failed
