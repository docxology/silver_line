from __future__ import annotations

from dataclasses import fields
from hashlib import sha256
import json
import math

from .records import ReleaseDeclaration, SuccessionItem


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def source_value(value: object) -> object:
    if isinstance(value, (SuccessionItem, ReleaseDeclaration)):
        return {f.name: source_value(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, (tuple, list, set, frozenset)):
        return sorted((source_value(v) for v in value), key=canonical_json)
    if value is None or isinstance(value, (str, bool, int)):
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
