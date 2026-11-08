from __future__ import annotations

from dataclasses import fields
from hashlib import sha256
import json
import math

from .records import ReleaseDeclaration, SuccessionItem

TEXT_CODE_UNITS = "silver_line.text-code-units/1"


def scalar_text(value: object) -> bool:
    """Whether a string contains only Unicode scalar values (including non-BMP)."""
    return isinstance(value, str) and not any(0xD800 <= ord(c) <= 0xDFFF for c in value)


def snapshot_value(value: object) -> object:
    """Encode malformed strings only; preserve valid JSON text and array order."""
    if isinstance(value, str) and not scalar_text(value):
        return {TEXT_CODE_UNITS: [ord(c) for c in value]}
    if isinstance(value, dict):
        if any(not scalar_text(key) for key in value):
            raise ValueError("snapshot object keys must be Unicode scalar text")
        return {key: snapshot_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [snapshot_value(item) for item in value]
    return value


def restore_snapshot(value: object) -> object:
    """Decode the native malformed-text marker without JSON surrogate folding."""
    if isinstance(value, dict):
        if TEXT_CODE_UNITS in value:
            points = value[TEXT_CODE_UNITS]
            if (
                set(value) != {TEXT_CODE_UNITS}
                or not isinstance(points, list)
                or not points
                or any(type(p) is not int or not 0 <= p <= 0x10FFFF for p in points)
                or not any(0xD800 <= p <= 0xDFFF for p in points)
            ):
                raise ValueError("invalid Silver text-code-units/1 snapshot marker")
            return "".join(chr(p) for p in points)
        return {key: restore_snapshot(item) for key, item in value.items()}
    if isinstance(value, list):
        return [restore_snapshot(item) for item in value]
    return value



def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def source_value(value: object) -> object:
    if isinstance(value, (SuccessionItem, ReleaseDeclaration)):
        return {f.name: source_value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, (tuple, list, set, frozenset)):
        return sorted((source_value(v) for v in value), key=canonical_json)
    if isinstance(value, str):
        return snapshot_value(value)
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    return {"unsupported_type": type(value).__module__ + "." + type(value).__qualname__}


def canonical_source(raw: object) -> str:
    if isinstance(raw, SuccessionItem):
        raw = (raw,)
    return canonical_json(source_value(raw))


def item_snapshot(item: SuccessionItem) -> dict[str, object]:
    return {
        "item_id": item.item_id, "description": item.description,
        "custodian": item.custodian, "tags": sorted(item.tags),
        "evidence": sorted(item.evidence), "release": source_value(item.release),
    }
