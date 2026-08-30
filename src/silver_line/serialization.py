"""Deterministic serialization and digesting for review and drift detection.

The digest is a review instrument: two reviewers holding the same digest are
talking about the same keepsake content, and an unexpected digest change is a
drift signal that the registry was edited. It carries no persistence or
permission semantics of any kind.
"""

from __future__ import annotations

import hashlib
import json

from .records import Keepsake, SuccessionVerdict


def canonical_registry(keepsakes: tuple[Keepsake, ...]) -> str:
    """Serialize keepsakes into stable JSON for review and comparison."""

    payload = [
        keepsake.canonical()
        for keepsake in sorted(keepsakes, key=lambda item: item.id)
    ]
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def registry_digest(keepsakes: tuple[Keepsake, ...]) -> str:
    """Return a SHA-256 digest of the canonical registry serialization."""

    return hashlib.sha256(canonical_registry(keepsakes).encode("utf-8")).hexdigest()


def canonical_verdict(verdict: SuccessionVerdict) -> str:
    """Serialize a verdict into stable JSON so results can be archived.

    Two identical readings of the same subject produce byte-identical output,
    which lets a verdict be diffed and cited in a review record.
    """

    payload = {
        "schema_version": "1.0",
        "status": verdict.status.value,
        "evaluated_as_of": verdict.evaluated_as_of,
        "registry_digest": verdict.registry_digest,
        "intake_notes": [
            {"disposition": note.disposition.value, "note": note.note}
            for note in verdict.intake_notes
        ],
        "findings": [
            {
                "keepsake_id": finding.keepsake_id,
                "status": finding.status.value,
                "reasons": list(finding.reasons),
            }
            for finding in verdict.findings
        ],
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def verdict_digest(verdict: SuccessionVerdict) -> str:
    """SHA-256 over the canonical verdict; the pointer an envelope carries."""

    return hashlib.sha256(canonical_verdict(verdict).encode("utf-8")).hexdigest()
