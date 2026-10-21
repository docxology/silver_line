from __future__ import annotations

from dataclasses import replace

from .enums import IntakeDisposition, KeepKind, ProvisionStatus, VerdictStatus
from .intake import clean_labels, intake, normalize_item, vocabulary_check
from .records import IntakeNote, Keepsake, ProvisionFinding, ReleaseDeclaration, SuccessionItem, SuccessionVerdict
from .registry import KEEPSAKE_TAG_VOCABULARY, SILVER_KEEPSAKES
from .serialization import registry_digest
from .snapshots import canonical_json, canonical_source, digest_text, item_snapshot
from .validation import registry_shape_error, validate_review_date
from .version import __version__


def _prepare(raw_items: object):
    if isinstance(raw_items, SuccessionItem):
        raw_items = (raw_items,)
    if not isinstance(raw_items, (list, tuple, set, frozenset)):
        items, notes = intake(raw_items)
        return items, list(notes), 0
    items = []
    notes = []
    for raw in raw_items:
        fallback_id = "input-" + digest_text(canonical_source(raw))
        if isinstance(raw, SuccessionItem) and raw.item_id == "":
            raw = replace(raw, item_id=fallback_id)
        item, item_notes = normalize_item(raw)
        item_id = item.item_id if item else fallback_id
        notes.extend(replace(n, item_id=item_id) for n in item_notes)
        if item is not None:
            tags, tag_notes = clean_labels(item.tags, "tag")
            evidence, evidence_notes = clean_labels(item.evidence, "evidence")
            notes.extend(replace(n, item_id=item_id)
                         for n in tag_notes + evidence_notes + vocabulary_check(tags))
            items.append(replace(item, tags=tags & KEEPSAKE_TAG_VOCABULARY, evidence=evidence))
    if not items:
        notes.append(IntakeNote(IntakeDisposition.SET_ASIDE, "scan set contained no usable declarations; the reading fails closed"))
    return tuple(sorted(items, key=lambda i: i.item_id)), notes, len(raw_items) - len(items)


def _release_error(item: SuccessionItem, matched: tuple[Keepsake, ...], review_date: str) -> str | None:
    release = item.release
    if not isinstance(release, ReleaseDeclaration):
        return "release must be a ReleaseDeclaration"
    if any(not isinstance(v, str) or not v.strip() or v != v.strip()
           for v in (release.item_id, release.declared_by, release.declared_on, release.source_ref)):
        return "release requires canonical item_id, declared_by, declared_on and source_ref"
    if release.item_id != item.item_id:
        return "release item_id does not match this item"
    try:
        validate_review_date(release.declared_on)
    except ValueError:
        return "release declared_on must be YYYY-MM-DD"
    if review_date and release.declared_on > review_date:
        return "release declared_on is after the review date"
    if not any(k.kind is KeepKind.LAPSE and k.may_lapse for k in matched):
        return "item has no applicable lapse eligibility"
    return None


def _finding(item: SuccessionItem, keepsake: Keepsake, released: bool) -> ProvisionFinding:
    if released and keepsake.kind is not KeepKind.RESTRAINT:
        return ProvisionFinding(keepsake.id, ProvisionStatus.DECLARED_RELEASE,
                                ("explicit scoped release declared; no retention failure inferred",
                                 "no permission for disclosure, destruction or transfer"), item.item_id)
    present = tuple(v for v in keepsake.required_evidence if v in item.evidence)
    missing = tuple(v for v in keepsake.required_evidence if v not in item.evidence)
    fields = ("custodian",) if keepsake.kind is KeepKind.ENTRUSTMENT and not item.custodian else ()
    if fields:
        return ProvisionFinding(keepsake.id, ProvisionStatus.NEEDS_REWORK,
                                ("missing declared field: custodian",) +
                                (("required evidence is missing: " + ", ".join(missing),) if missing else ()),
                                item.item_id, fields + missing)
    if not missing:
        return ProvisionFinding(keepsake.id, ProvisionStatus.KEPT,
                                ("required evidence is present: " + ", ".join(present),), item.item_id)
    reasons = ("required evidence is missing: " + ", ".join(missing),)
    if keepsake.may_lapse:
        return ProvisionFinding(keepsake.id, ProvisionStatus.NEEDS_PROVISION,
                                reasons + ("lapse eligible but not yet declared; unresolved, not a retention defect",),
                                item.item_id, missing)
    if present:
        reasons += ("evidence already present: " + ", ".join(present),)
    return ProvisionFinding(keepsake.id, ProvisionStatus.NEEDS_REWORK, reasons, item.item_id, missing)


def _overall(findings: tuple[ProvisionFinding, ...]) -> VerdictStatus:
    statuses = {f.status for f in findings}
    for status in (ProvisionStatus.NEEDS_REWORK, ProvisionStatus.NEEDS_PROVISION, ProvisionStatus.DECLARED_RELEASE):
        if status in statuses:
            return VerdictStatus(status.value)
    return VerdictStatus.KEPT if findings else VerdictStatus.OUTSIDE_SCOPE


def _read(raw_items: object, keepsakes: tuple[Keepsake, ...], evaluated_as_of: str, subject_id: str):
    validate_review_date(evaluated_as_of)
    if not isinstance(subject_id, str) or not subject_id.strip() or subject_id != subject_id.strip():
        raise ValueError("subject_id must be nonblank canonical text")
    source_digest = digest_text(canonical_source(raw_items))
    items, notes, rejected = _prepare(raw_items)
    declaration_digest = digest_text(canonical_json([item_snapshot(i) for i in items]))
    error = registry_shape_error(keepsakes)
    digest = "" if error else registry_digest(keepsakes)
    duplicate_ids = sorted({i.item_id for i in items if sum(j.item_id == i.item_id for j in items) > 1})
    if duplicate_ids:
        notes.extend(IntakeNote(IntakeDisposition.SET_ASIDE, "duplicate item_id; entire scan set rejected", i)
                     for i in duplicate_ids)
        rejected += len(items)
        items = ()
    if error:
        notes.append(IntakeNote(IntakeDisposition.SET_ASIDE,
                                "keepsake registry is not safe to score and must be repaired: " + error))
    findings = []
    unmatched = 0
    if not error and not duplicate_ids:
        for item in items:
            matched = tuple(sorted((k for k in keepsakes if k.tags & item.tags), key=lambda k: k.id))
            if not matched:
                unmatched += 1
                notes.append(IntakeNote(IntakeDisposition.SET_ASIDE, "no applicable reviewed keepsakes", item.item_id))
            released = False
            if item.release is not None:
                release_error = _release_error(item, matched, evaluated_as_of)
                if release_error:
                    findings.append(ProvisionFinding("release-declaration", ProvisionStatus.NEEDS_REWORK,
                                                     (release_error,), item.item_id, ("release",)))
                else:
                    released = True
            findings.extend(_finding(item, k, released) for k in matched)
    findings = tuple(sorted(findings, key=lambda f: (f.item_id, f.keepsake_id)))
    scope = "PARTIAL" if rejected or unmatched else ("COMPLETE" if items else "EMPTY")
    if error:
        scope = "UNSCORABLE"
    verdict = SuccessionVerdict(
        status=VerdictStatus.NEEDS_REWORK if error or duplicate_ids else _overall(findings),
        findings=findings, intake_notes=tuple(sorted(notes, key=lambda n: (n.item_id, n.disposition.value, n.note))),
        evaluated_as_of=evaluated_as_of, registry_digest=digest, subject_id=subject_id,
        declaration_digest=declaration_digest, source_digest=source_digest,
        evaluator_version=__version__, registry_version=__version__, accepted_count=len(items),
        rejected_count=rejected, unmatched_count=unmatched, reading_scope=scope,
    )
    return verdict, verdict.findings


def read_succession(
    raw_items: object, keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES, *,
    evaluated_as_of: str = "", subject_id: str = "UNSPECIFIED",
) -> SuccessionVerdict:
    return _read(raw_items, keepsakes, evaluated_as_of, subject_id)[0]


def read_succession_with_findings(
    raw_items: object, keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES, *,
    evaluated_as_of: str = "", subject_id: str = "UNSPECIFIED",
) -> tuple[SuccessionVerdict, tuple[ProvisionFinding, ...]]:
    return _read(raw_items, keepsakes, evaluated_as_of, subject_id)
