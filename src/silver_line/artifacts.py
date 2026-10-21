from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .evaluator import _prepare, read_succession
from .records import ReleaseDeclaration, SuccessionItem, SuccessionVerdict
from .registry import SILVER_KEEPSAKES
from .serialization import canonical_registry, canonical_verdict, verdict_digest
from .snapshots import canonical_json, canonical_source, digest_text, item_snapshot

NONCLAIMS = (
    "I report declared custody and provision within the qualified reading scope only.",
    "I do not verify labels, custody, acceptance, legal succession or consent.",
    "No status guarantees persistence, survival, safety or quality.",
    "No status or scoped release authorizes disclosure, destruction, transfer or any action.",
    "I do not rank, merge, score or compensate other line instruments.",
)


def fixture_items(fixture: dict) -> tuple[SuccessionItem, ...]:
    items = []
    for row in fixture["items"]:
        release = ReleaseDeclaration(**row["release"]) if row.get("release") else None
        items.append(SuccessionItem(
            description=row["description"], custodian=row["custodian"],
            tags=frozenset(row["tags"]), evidence=frozenset(row["evidence"]),
            item_id=row["item_id"], release=release,
        ))
    return tuple(items)


def build_envelope(verdict: SuccessionVerdict, source_refs: tuple[str, ...]) -> dict:
    if not verdict.evaluated_as_of or verdict.subject_id == "UNSPECIFIED":
        raise ValueError("published envelopes require an explicit subject and review date")
    if not verdict.registry_digest or not source_refs:
        raise ValueError("published envelopes require a valid registry and immutable source references")
    pattern = re.compile(r"sha256:([0-9a-f]{64}):data/snapshots/\1\.json")
    matches = [pattern.fullmatch(ref) for ref in source_refs]
    if not all(matches):
        raise ValueError("source references must be immutable SHA-256 snapshot paths")
    digests = {ref.split(":", 2)[1] for ref in source_refs}
    if not {verdict.registry_digest, verdict.source_digest, verdict.declaration_digest} <= digests:
        raise ValueError("source references must bind registry, source and normalized declarations")
    return {
        "line_id": "silver_line", "native_status": verdict.status.value,
        "registry_digest": verdict.registry_digest, "registry_version": verdict.registry_version,
        "report_ref": verdict_digest(verdict), "review_date": verdict.evaluated_as_of,
        "schema_version": "line.report-envelope/1.0", "subject_id": verdict.subject_id,
        "source_snapshot_refs": sorted(set(source_refs)),
        "scope_and_nonclaims": list(NONCLAIMS) + [
            f"reading_scope={verdict.reading_scope}; accepted={verdict.accepted_count}; "
            f"rejected={verdict.rejected_count}; unmatched={verdict.unmatched_count}"],
    }


def validate_envelope(envelope: dict, verdict: SuccessionVerdict, source_refs: tuple[str, ...]) -> None:
    if envelope != build_envelope(verdict, source_refs):
        raise ValueError("envelope differs from regenerated report identity, status or scope")


def artifact_payloads(fixture: dict) -> tuple[dict, dict[str, str]]:
    items = fixture_items(fixture)
    verdict = read_succession(items, evaluated_as_of=fixture["review_date"], subject_id=fixture["subject_id"])
    normalized, _, _ = _prepare(items)
    snapshot_texts = (
        canonical_json(fixture), canonical_source(items),
        canonical_json([item_snapshot(i) for i in normalized]), canonical_registry(SILVER_KEEPSAKES),
    )
    files = {f"data/snapshots/{digest_text(t)}.json": t for t in snapshot_texts}
    refs = tuple(f"sha256:{digest_text(t)}:data/snapshots/{digest_text(t)}.json" for t in snapshot_texts)
    files[f"data/reports/{verdict_digest(verdict)}.json"] = canonical_verdict(verdict)
    return build_envelope(verdict, refs), files


def build_artifacts(root: Path, *, check: bool = False) -> tuple[str, ...]:
    fixtures = sorted((root / "data/fixtures").glob("*.json"))
    if not fixtures:
        raise ValueError("no canonical fixtures; artifact check fails closed")
    outputs = {}
    for path in fixtures:
        envelope, files = artifact_payloads(json.loads(path.read_text(encoding="utf-8")))
        outputs.update(files)
        outputs[f"data/envelopes/{path.name}"] = json.dumps(envelope, indent=2, sort_keys=True) + "\n"
    expected_envelopes = {p.name for p in fixtures}
    if {p.name for p in (root / "data/envelopes").glob("*.json")} - expected_envelopes:
        raise ValueError("envelope has no canonical fixture")
    for name, content in sorted(outputs.items()):
        path = root / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"artifact drift: {name}")
        else:
            if path.exists() and name.startswith(("data/snapshots/", "data/reports/")):
                if path.read_text(encoding="utf-8") != content:
                    raise ValueError(f"immutable artifact differs: {name}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    return tuple(sorted(outputs))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    outputs = build_artifacts(root, check=args.check)
    print(f"{'checked' if args.check else 'generated'} {len(outputs)} report, snapshot and envelope artifacts")


if __name__ == "__main__":
    main()
