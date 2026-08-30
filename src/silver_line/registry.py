"""The versioned Silver Line keepsake registry.

Every entry names one thing worth keeping, the tags that make it applicable,
and the evidence labels a successor could inspect. The registry is a memory
instrument: it describes how to keep work honestly - including naming what is
allowed to lapse - and never guarantees that anything persists.
"""

from __future__ import annotations

from .enums import KeepKind
from .records import Keepsake

#: The reviewed tag vocabulary. Keepsake tags outside this set are
#: unreviewable drift; the invariants battery enforces membership.
KEEPSAKE_TAG_VOCABULARY: frozenset[str] = frozenset(
    {"artifact", "relationship", "institution", "practice", "record"}
)

SILVER_KEEPSAKES: tuple[Keepsake, ...] = (
    Keepsake(
        "question-first-succession",
        "Name what is being kept before how",
        "State the thing preserved, its boundary, and why it outlives the keeper.",
        frozenset({"record", "practice"}),
        ("succession_statement",),
        KeepKind.RETENTION,
    ),
    Keepsake(
        "entrusted-to-named-custodian",
        "Entrust each kept thing to a named custodian",
        "A keepsake without a custodian is a wish; name the person or role that carries it.",
        frozenset({"relationship", "institution", "record"}),
        ("custodian_name", "custodian_acknowledgement"),
        KeepKind.ENTRUSTMENT,
    ),
    Keepsake(
        "inspectable-handoff",
        "Make the handoff inspectable by its receiver",
        "A successor should recover purpose, location, and next action without private context.",
        frozenset({"artifact", "record"}),
        ("handoff_note", "location_pointer"),
        KeepKind.TRANSMISSION,
    ),
    Keepsake(
        "lapse-named",
        "Name what is allowed to lapse",
        "Declare which items may be released so retention attention is not spread falsely thin.",
        frozenset({"record", "practice"}),
        ("lapse_declaration",),
        KeepKind.LAPSE,
        True,
    ),
    Keepsake(
        "origin-recorded",
        "Record where each kept thing came from",
        "State provenance so a successor can judge what the kept thing is and is not.",
        frozenset({"artifact", "record", "institution"}),
        ("origin_note",),
        KeepKind.RETENTION,
    ),
    Keepsake(
        "renewal-cadence",
        "Give living keepsakes a review cadence",
        "Relationships and practices decay silently; set when each is next reviewed.",
        frozenset({"relationship", "practice", "institution"}),
        ("review_cadence", "last_reviewed"),
        KeepKind.ENTRUSTMENT,
    ),
    Keepsake(
        "no-infallible-archive",
        "Refuse the infallible-archive claim",
        "Preservation describes intent and custody, never a guarantee of persistence.",
        frozenset({"artifact", "record"}),
        ("drift_acknowledgement",),
        KeepKind.RESTRAINT,
        True,
    ),
    Keepsake(
        "succession-rehearsed",
        "Rehearse the succession at least once",
        "A handoff that has never been practised is a plan, not a proven route.",
        frozenset({"practice", "relationship"}),
        ("rehearsal_record",),
        KeepKind.TRANSMISSION,
    ),
    Keepsake(
        "negative-space-kept",
        "Record what was deliberately not kept",
        "A documented release narrows the successor's search space and honours the choice.",
        frozenset({"record", "practice"}),
        ("release_log",),
        KeepKind.LAPSE,
        True,
    ),
    Keepsake(
        "review-before-entrustment",
        "Invite review before the entrustment is relied on",
        "A second reader can expose a custodian or a route the keeper stopped seeing.",
        frozenset({"relationship", "institution"}),
        ("review_note",),
        KeepKind.ENTRUSTMENT,
    ),
    Keepsake(
        "versioned-keepsake",
        "Keep changes to a kept thing reviewable",
        "Record each increment so its history can be read, reverted, and entrusted intact.",
        frozenset({"artifact", "record"}),
        ("version_log",),
        KeepKind.RETENTION,
    ),
)


def registry_ids() -> tuple[str, ...]:
    """Return registry ids in declaration order."""

    return tuple(keepsake.id for keepsake in SILVER_KEEPSAKES)
