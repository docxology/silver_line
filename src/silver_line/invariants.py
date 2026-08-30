"""Offline invariant checks over the Silver Line's own declaration.

Every check takes the keepsake registry as an argument and names no specific
entry, so the same battery runs over a custom registry unchanged. Each check
fails closed: a violation is a named result, never silence.
"""

from __future__ import annotations

from dataclasses import dataclass

from .enums import KeepKind
from .records import Keepsake
from .registry import KEEPSAKE_TAG_VOCABULARY


@dataclass(frozen=True)
class CheckResult:
    """One named invariant with a pass/fail and a reason trail."""

    name: str
    passed: bool
    reasons: tuple[str, ...]


def _result(name: str, reasons: list[str]) -> CheckResult:
    return CheckResult(name, not reasons, tuple(reasons))


def check_nonempty_registry(keepsakes: tuple[Keepsake, ...]) -> CheckResult:
    """Fail closed on an empty registry: nothing declared, nothing readable."""

    if keepsakes:
        return _result("nonempty_registry", [])
    return _result("nonempty_registry", ["registry is empty; fail closed"])


def check_unique_keepsake_ids(keepsakes: tuple[Keepsake, ...]) -> CheckResult:
    seen: set[str] = set()
    duplicates: list[str] = []
    for keepsake in keepsakes:
        if keepsake.id in seen and keepsake.id not in duplicates:
            duplicates.append(keepsake.id)
        seen.add(keepsake.id)
    return _result(
        "unique_keepsake_ids", [f"duplicate ids: {sorted(duplicates)}"] if duplicates else []
    )


def check_tags_in_vocabulary(keepsakes: tuple[Keepsake, ...]) -> CheckResult:
    unknown: set[str] = set()
    for keepsake in keepsakes:
        unknown |= keepsake.tags - KEEPSAKE_TAG_VOCABULARY
    return _result(
        "tags_in_vocabulary",
        [f"tags outside the reviewed vocabulary: {sorted(unknown)}"] if unknown else [],
    )


def check_required_evidence_declared(keepsakes: tuple[Keepsake, ...]) -> CheckResult:
    blank = [keepsake.id for keepsake in keepsakes if not keepsake.required_evidence]
    return _result(
        "required_evidence_declared",
        [f"keepsakes with no required evidence: {sorted(blank)}"] if blank else [],
    )


def check_lapse_families_present(keepsakes: tuple[Keepsake, ...]) -> CheckResult:
    """The set must name what may lapse; retention-only is drift."""

    families = {keepsake.kind for keepsake in keepsakes}
    missing = [kind.value for kind in KeepKind if kind not in families]
    return _result(
        "lapse_families_present",
        [f"keep kinds not represented: {missing}"] if missing else [],
    )


def all_invariants(
    keepsakes: tuple[Keepsake, ...],
) -> tuple[CheckResult, ...]:
    """Run the whole offline battery over a keepsake registry."""

    return (
        check_nonempty_registry(keepsakes),
        check_unique_keepsake_ids(keepsakes),
        check_tags_in_vocabulary(keepsakes),
        check_required_evidence_declared(keepsakes),
        check_lapse_families_present(keepsakes),
    )
