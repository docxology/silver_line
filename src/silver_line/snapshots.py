from __future__ import annotations

from dataclasses import fields
from hashlib import sha256
import json
import math

from .records import ReleaseDeclaration, SuccessionItem

SOURCE_CODEC = "silver.source/1"


def scalar_text(value: object) -> bool:
    """Whether a string contains only Unicode scalar values (including non-BMP)."""
    return isinstance(value, str) and not any(0xD800 <= ord(c) <= 0xDFFF for c in value)


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def source_value(value: object) -> object:
    """Encode supported native values without interpreting literal dictionaries.

    Unsupported producers have diagnostic identities only, not replay support.
    No class names from a snapshot are ever imported or instantiated.
    """
    if type(value) in (SuccessionItem, ReleaseDeclaration):
        return {
            "kind": type(value).__name__,
            "value": {
                f.name: source_value(getattr(value, f.name)) for f in fields(value)
            },
        }
    if type(value) in (tuple, list, set, frozenset):
        items = [source_value(v) for v in value]
        if type(value) in (set, frozenset):
            items.sort(key=canonical_json)
        return {"kind": type(value).__name__, "value": items}
    if type(value) is dict:
        return {
            "kind": "dict",
            "value": [[source_value(k), source_value(v)] for k, v in value.items()],
        }
    if type(value) is str:
        if scalar_text(value):
            return value
        return {"kind": "text-code-units", "value": [ord(c) for c in value]}
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    return {
        "kind": "unsupported",
        "value": type(value).__module__ + "." + type(value).__qualname__,
    }


def canonical_source(raw: object) -> str:
    """Return a versioned source snapshot with canonical root scan semantics."""
    if isinstance(raw, SuccessionItem):
        raw = (raw,)
    if type(raw) in (list, tuple, set, frozenset):
        value = {
            "kind": "scan",
            "value": sorted((source_value(item) for item in raw), key=canonical_json),
        }
    else:
        value = source_value(raw)
    return canonical_json({"codec": SOURCE_CODEC, "value": value})


def _restore_value(value: object) -> object:
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is str and scalar_text(value):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if type(value) is not dict or set(value) != {"kind", "value"}:
        raise ValueError("invalid Silver source value")
    kind, payload = value["kind"], value["value"]
    if type(kind) is not str:
        raise ValueError("invalid Silver source kind")
    if kind == "text-code-units":
        if (
            type(payload) is not list
            or not payload
            or any(type(p) is not int or not 0 <= p <= 0x10FFFF for p in payload)
            or not any(0xD800 <= p <= 0xDFFF for p in payload)
        ):
            raise ValueError("invalid Silver source text-code-units")
        return "".join(chr(p) for p in payload)
    if kind in ("SuccessionItem", "ReleaseDeclaration"):
        record = SuccessionItem if kind == "SuccessionItem" else ReleaseDeclaration
        if type(payload) is not dict or set(payload) != {
            f.name for f in fields(record)
        }:
            raise ValueError("invalid Silver source record fields")
        return record(**{key: _restore_value(v) for key, v in payload.items()})
    if kind in ("list", "tuple", "set", "frozenset"):
        if type(payload) is not list:
            raise ValueError("invalid Silver source container")
        items = [_restore_value(v) for v in payload]
        if kind == "list":
            return items
        if kind == "tuple":
            return tuple(items)
        try:
            result = set(items) if kind == "set" else frozenset(items)
        except TypeError as exc:
            raise ValueError("unhashable Silver source set member") from exc
        if len(result) != len(items):
            raise ValueError("duplicate Silver source set member")
        return result
    if kind == "dict":
        if type(payload) is not list:
            raise ValueError("invalid Silver source dictionary")
        result = {}
        for pair in payload:
            if type(pair) is not list or len(pair) != 2:
                raise ValueError("invalid Silver source dictionary entry")
            key, item = (_restore_value(v) for v in pair)
            try:
                if key in result:
                    raise ValueError("duplicate Silver source dictionary key")
                result[key] = item
            except TypeError as exc:
                raise ValueError("unhashable Silver source dictionary key") from exc
        return result
    raise ValueError(
        "unsupported Silver source kind; replay requires supported native values"
    )


def restore_source(snapshot: object) -> object:
    """Decode only silver.source/1; historical snapshots need their own producer.

    Pass a JSON-decoded snapshot, then pass its restored native scan directly to
    read_succession. This is not JSON fixture admission or generic object loading.
    """
    if (
        type(snapshot) is not dict
        or set(snapshot) != {"codec", "value"}
        or snapshot["codec"] != SOURCE_CODEC
    ):
        raise ValueError("expected a versioned silver.source/1 snapshot")
    value = snapshot["value"]
    if (
        type(value) is dict
        and set(value) == {"kind", "value"}
        and value["kind"] == "scan"
    ):
        if type(value["value"]) is not list:
            raise ValueError("invalid Silver source scan")
        return tuple(_restore_value(item) for item in value["value"])
    return _restore_value(value)


def item_snapshot(item: SuccessionItem) -> dict[str, object]:
    return {
        "item_id": item.item_id,
        "description": item.description,
        "custodian": item.custodian,
        "tags": sorted(item.tags),
        "evidence": sorted(item.evidence),
        "release": source_value(item.release),
    }
