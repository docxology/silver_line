from __future__ import annotations

from datetime import date

from .enums import KeepKind
from .records import Keepsake
from .registry import KEEPSAKE_TAG_VOCABULARY


def validate_review_date(value: str) -> str:
    if value == "":
        return value
    if not isinstance(value, str):
        raise ValueError("review date must be YYYY-MM-DD or empty for undated")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("review date must be YYYY-MM-DD or empty for undated") from exc
    if parsed.isoformat() != value:
        raise ValueError("review date must use canonical YYYY-MM-DD")
    return value


def registry_shape_error(keepsakes: tuple[Keepsake, ...]) -> str | None:
    if not isinstance(keepsakes, tuple) or not keepsakes:
        return "keepsake registry is empty or is not a tuple; fail closed"
    seen_ids: set[str] = set()
    errors: list[str] = []
    for keepsake in keepsakes:
        if not isinstance(keepsake, Keepsake):
            errors.append("keepsake registry entry is not a Keepsake record")
            continue
        if any(not isinstance(v, str) or not v.strip() or v != v.strip()
               for v in (keepsake.id, keepsake.title, keepsake.wire)):
            errors.append("keepsake registry entry has blank or non-text or noncanonical fields")
            continue
        if keepsake.id in seen_ids:
            errors.append(f"keepsake registry contains duplicate id '{keepsake.id}'")
        seen_ids.add(keepsake.id)
        if (not isinstance(keepsake.tags, frozenset) or not keepsake.tags
                or any(not isinstance(t, str) or not t.strip() for t in keepsake.tags)):
            errors.append(f"keepsake '{keepsake.id}' has malformed tags")
        elif not keepsake.tags <= KEEPSAKE_TAG_VOCABULARY:
            errors.append(f"keepsake '{keepsake.id}' has tags outside the reviewed vocabulary")
        if (not isinstance(keepsake.required_evidence, tuple) or not keepsake.required_evidence
                or any(not isinstance(v, str) or not v or v != v.strip().lower()
                       for v in keepsake.required_evidence)):
            errors.append(f"keepsake '{keepsake.id}' has malformed required evidence")
        elif len(set(keepsake.required_evidence)) != len(keepsake.required_evidence):
            errors.append(f"keepsake '{keepsake.id}' has duplicate required evidence")
        if not isinstance(keepsake.kind, KeepKind):
            errors.append(f"keepsake '{keepsake.id}' kind is not a KeepKind member")
        if not isinstance(keepsake.may_lapse, bool):
            errors.append(f"keepsake '{keepsake.id}' has a non-boolean lapse flag")
        elif keepsake.may_lapse and keepsake.kind is not KeepKind.LAPSE:
            errors.append(f"keepsake '{keepsake.id}' only LAPSE requirements may permit lapse")
    return "; ".join(sorted(errors)) or None
