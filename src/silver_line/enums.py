"""Enumerations for succession outcomes, keepsake families, and intake dispositions.

These name the verdict vocabulary of the Silver Line. They describe how a
declared succession picture reads at a stated review date; they never assert
that anything is safe, true, or guaranteed to persist.
"""

from __future__ import annotations

from enum import Enum


class ProvisionStatus(str, Enum):
    """Outcome for a single keepsake that applies to a succession reading."""

    KEPT = "KEPT"
    NEEDS_PROVISION = "NEEDS_PROVISION"
    NEEDS_REWORK = "NEEDS_REWORK"


class VerdictStatus(str, Enum):
    """Overall verdict for a succession reading."""

    KEPT = "KEPT"
    NEEDS_PROVISION = "NEEDS_PROVISION"
    NEEDS_REWORK = "NEEDS_REWORK"
    OUTSIDE_SCOPE = "OUTSIDE_SCOPE"


class KeepKind(str, Enum):
    """The family of succession work a keepsake belongs to.

    Families exist so the registry can be reviewed for balance: a registry
    that only rewards retention but never names what may lapse has drifted
    from the Silver Line's purpose - keeping honestly includes letting go.
    """

    RETENTION = "RETENTION"
    ENTRUSTMENT = "ENTRUSTMENT"
    TRANSMISSION = "TRANSMISSION"
    LAPSE = "LAPSE"
    RESTRAINT = "RESTRAINT"


class IntakeDisposition(str, Enum):
    """What the staged intake did with one incoming item."""

    ACCEPTED = "ACCEPTED"
    SET_ASIDE = "SET_ASIDE"
