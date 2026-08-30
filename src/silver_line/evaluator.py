"""Staged evaluation of succession declarations.

Evaluation is deliberately staged: intake normalization runs first, so
hostile or malformed input (non-string labels, a blank description, an
unusable custodian) is set aside in ``intake_notes`` instead of crashing or
silently passing. Only then are keepsakes matched by tag and scored against
the declared evidence set. The output describes declared provision and review
gaps; it never turns labels into persistence, safety, or permission for
anything.
"""

from __future__ import annotations

from .enums import IntakeDisposition, ProvisionStatus, VerdictStatus
from .intake import clean_labels, intake, vocabulary_check
from .records import IntakeNote, Keepsake, ProvisionFinding, SuccessionItem, SuccessionVerdict
from .registry import SILVER_KEEPSAKES
from .serialization import registry_digest


def _registry_shape_error(keepsakes: tuple[Keepsake, ...]) -> str | None:
    """Return a blocking note when a registry cannot be safely scored."""

    seen_ids: set[str] = set()
    for index, keepsake in enumerate(keepsakes):
        if not isinstance(keepsake, Keepsake):
            return f"keepsake registry entry {index} is not a Keepsake record"
        if any(
            not isinstance(value, str) or not value.strip()
            for value in (keepsake.id, keepsake.title, keepsake.wire)
        ):
            return f"keepsake registry entry {index} has blank or non-text fields"
        if keepsake.id in seen_ids:
            return f"keepsake registry contains duplicate id '{keepsake.id}'"
        seen_ids.add(keepsake.id)
        if (
            not isinstance(keepsake.tags, frozenset)
            or not keepsake.tags
            or any(not isinstance(tag, str) or not tag.strip() for tag in keepsake.tags)
        ):
            return f"keepsake '{keepsake.id}' has malformed tags"
        if (
            not isinstance(keepsake.required_evidence, tuple)
            or not keepsake.required_evidence
            or any(
                not isinstance(label, str) or not label.strip()
                for label in keepsake.required_evidence
            )
        ):
            return f"keepsake '{keepsake.id}' has malformed required evidence"
        if not isinstance(keepsake.may_lapse, bool):
            return f"keepsake '{keepsake.id}' has a non-boolean lapse flag"
    return None


def _surfaces(
    keepsake: Keepsake,
    declared: frozenset[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split one keepsake's required labels into present and missing."""

    present = tuple(item for item in keepsake.required_evidence if item in declared)
    missing = tuple(item for item in keepsake.required_evidence if item not in declared)
    return present, missing


def _finding(
    keepsake: Keepsake, present: tuple[str, ...], missing: tuple[str, ...]
) -> ProvisionFinding:
    """Project one keepsake's surfaces onto a status with a reasons trail."""

    if not missing:
        return ProvisionFinding(
            keepsake.id,
            ProvisionStatus.KEPT,
            ("required evidence is present: " + ", ".join(present),),
        )
    if keepsake.may_lapse:
        return ProvisionFinding(
            keepsake.id,
            ProvisionStatus.NEEDS_PROVISION,
            (
                "required evidence is missing: " + ", ".join(missing),
                "this keepsake may lapse; a gap is a declared release, not a defect",
            ),
        )
    reasons = ["required evidence is missing: " + ", ".join(missing)]
    if present:
        reasons.append("evidence already present: " + ", ".join(present))
    return ProvisionFinding(keepsake.id, ProvisionStatus.NEEDS_REWORK, tuple(reasons))


def _overall(findings: tuple[ProvisionFinding, ...]) -> VerdictStatus:
    statuses = {finding.status for finding in findings}
    if ProvisionStatus.NEEDS_REWORK in statuses:
        return VerdictStatus.NEEDS_REWORK
    if ProvisionStatus.NEEDS_PROVISION in statuses:
        return VerdictStatus.NEEDS_PROVISION
    return VerdictStatus.KEPT if findings else VerdictStatus.OUTSIDE_SCOPE


def _note(disposition: IntakeDisposition, text: str) -> IntakeNote:
    return IntakeNote(disposition, text)


def _evaluate(
    items: tuple[SuccessionItem, ...],
    intake_notes: tuple[IntakeNote, ...],
    keepsakes: tuple[Keepsake, ...],
) -> tuple[SuccessionVerdict, tuple[ProvisionFinding, ...]]:
    """Run the staged evaluation once behind the public forms."""

    notes: list[IntakeNote] = list(intake_notes)
    shape_error = (
        _registry_shape_error(keepsakes)
        if keepsakes
        else "keepsake registry is empty; fail closed"
    )
    if shape_error:
        digest = ""
        notes.append(
            _note(
                IntakeDisposition.SET_ASIDE,
                f"keepsake registry is not safe to score and must be repaired: {shape_error}",
            )
        )
    else:
        try:
            digest = registry_digest(keepsakes)
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            digest = ""
            notes.append(
                _note(
                    IntakeDisposition.SET_ASIDE,
                    f"keepsake registry could not be digested and must be repaired: {exc}",
                )
            )
    if not digest:
        return (
            SuccessionVerdict(
                VerdictStatus.NEEDS_REWORK, (), tuple(notes), "", digest
            ),
            (),
        )
    findings: list[ProvisionFinding] = []
    for item in items:
        tags, tag_notes = clean_labels(item.tags, "tag")
        notes.extend(tag_notes)
        notes.extend(vocabulary_check(tags))
        declared, evidence_notes = clean_labels(item.evidence, "evidence")
        notes.extend(evidence_notes)
        matched = tuple(keepsake for keepsake in keepsakes if keepsake.tags & tags)
        for keepsake in matched:
            present, missing = _surfaces(keepsake, declared)
            findings.append(_finding(keepsake, present, missing))
    verdict = SuccessionVerdict(
        _overall(tuple(findings)),
        tuple(findings),
        tuple(notes),
        "",
        digest,
    )
    return verdict, tuple(findings)


def read_succession(
    raw_items: object,
    keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES,
) -> SuccessionVerdict:
    """Read a scan set of succession declarations against the Silver registry.

    - An empty or entirely malformed scan set fails closed as
      ``OUTSIDE_SCOPE`` with intake notes, never a favourable default.
    - A registry that cannot be safely scored fails closed as ``NEEDS_REWORK``
      with no findings and an intake note.
    - Tags outside the reviewed vocabulary are set aside from matching and
      recorded; they are never silently accepted.
    - The verdict describes declared provision and review gaps only. It is
      never a guarantee of persistence and never permission for anything.
    """

    items, notes = intake(raw_items)
    verdict, _findings_unused = _evaluate(items, notes, keepsakes)
    return verdict


def read_succession_with_findings(
    raw_items: object,
    keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES,
) -> tuple[SuccessionVerdict, tuple[ProvisionFinding, ...]]:
    """Read the scan set and also return each finding.

    The verdict is exactly what ``read_succession`` returns for the same
    arguments - one shared staged implementation, not a second evaluator.
    """

    items, notes = intake(raw_items)
    return _evaluate(items, notes, keepsakes)
