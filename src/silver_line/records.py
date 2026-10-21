"""Frozen record types for keepsakes, succession subjects, and verdicts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .enums import IntakeDisposition, KeepKind, ProvisionStatus, VerdictStatus


@dataclass(frozen=True)
class Keepsake:
    """A declared item of kept work: what it is, who it is entrusted to,
    and the evidence labels a successor could inspect.

    ``may_lapse`` is registry policy eligibility, never a subject's decision.
    """

    id: str
    title: str
    wire: str
    tags: frozenset[str]
    required_evidence: tuple[str, ...]
    kind: KeepKind = KeepKind.RETENTION
    may_lapse: bool = False

    def canonical(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "wire": self.wire,
            "tags": sorted(self.tags),
            "required_evidence": list(self.required_evidence),
            "kind": self.kind.value,
            "may_lapse": self.may_lapse,
        }


@dataclass(frozen=True)
class ReleaseDeclaration:
    item_id: str
    declared_by: str
    declared_on: str
    source_ref: str


@dataclass(frozen=True)
class SuccessionItem:
    """A self-declared item of kept work assessed against the Silver registry.

    ``custodian`` names who the item is entrusted to; an empty custodian is a
    review gap, not an error. ``evidence`` is the declared label set.
    """

    description: str
    custodian: str = ""
    tags: frozenset[str] = frozenset()
    evidence: frozenset[str] = frozenset()
    item_id: str = ""
    release: ReleaseDeclaration | None = None


@dataclass(frozen=True)
class IntakeNote:
    """One staged-intake observation: what was accepted, what was set aside, why."""

    disposition: IntakeDisposition
    note: str
    item_id: str = ""


@dataclass(frozen=True)
class ProvisionFinding:
    """One keepsake-level provision status with a reviewable reason trail."""

    keepsake_id: str
    status: ProvisionStatus
    reasons: tuple[str, ...]
    item_id: str = ""
    missing_fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class SuccessionVerdict:
    """A complete succession verdict over one subject's declared items.

    ``intake_notes`` records normalization and intake observations (malformed
    labels, set-aside items, blocking description defects).
    ``evaluated_as_of`` is the ISO review date the reading used, and
    ``registry_digest`` pins the exact keepsake content that produced it.
    """

    status: VerdictStatus
    findings: tuple[ProvisionFinding, ...] = ()
    intake_notes: tuple[IntakeNote, ...] = field(default_factory=tuple)
    evaluated_as_of: str = ""
    registry_digest: str = ""
    subject_id: str = "UNSPECIFIED"
    declaration_digest: str = ""
    source_digest: str = ""
    evaluator_version: str = ""
    registry_version: str = ""
    accepted_count: int = 0
    rejected_count: int = 0
    unmatched_count: int = 0
    reading_scope: str = "EMPTY"
