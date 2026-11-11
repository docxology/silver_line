"""The invariant battery over the Silver declaration and negative controls."""

from __future__ import annotations

from dataclasses import replace

import pytest

from silver_line.enums import KeepKind
from silver_line.invariants import all_invariants, check_unique_keepsake_ids
from silver_line.records import Keepsake
from silver_line.registry import SILVER_KEEPSAKES


def test_all_invariants_pass_on_the_declaration() -> None:
    results = all_invariants(SILVER_KEEPSAKES)
    assert results
    for result in results:
        assert result.passed, (result.name, result.reasons)


def test_empty_registry_stops_at_named_shape_failure() -> None:
    results = all_invariants(())
    assert [(r.name, r.passed) for r in results] == [("runtime_registry_shape", False)]
    assert results[0].reasons


def test_duplicate_ids_fail() -> None:
    keepsake = SILVER_KEEPSAKES[0]
    result = check_unique_keepsake_ids((keepsake, keepsake))
    assert not result.passed


def test_unknown_tag_fails_structural_admission() -> None:
    bad = (Keepsake("x", "t", "w", frozenset({"zzz"}), ("a",)),)
    results = all_invariants(bad)
    assert [(r.name, r.passed) for r in results] == [("runtime_registry_shape", False)]
    assert results[0].reasons


def test_lapse_family_missing_fails() -> None:
    retention_only = tuple(
        keepsake for keepsake in SILVER_KEEPSAKES if keepsake.kind is not KeepKind.LAPSE
    )
    results = all_invariants(retention_only)
    failed = {r.name for r in results if not r.passed}
    assert "lapse_families_present" in failed


@pytest.mark.parametrize(
    "registry",
    [
        (None,),
        ({"id": "not-a-record"},),
        (replace(SILVER_KEEPSAKES[0], tags=None),),
        (replace(SILVER_KEEPSAKES[0], kind="RETENTION"),),
        (replace(SILVER_KEEPSAKES[0], required_evidence=None),),
    ],
)
def test_structural_failure_never_runs_shape_dependent_checks(registry):
    results = all_invariants(registry)
    assert [(r.name, r.passed) for r in results] == [("runtime_registry_shape", False)]
    assert results[0].reasons
