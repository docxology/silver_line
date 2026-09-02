"""Silver Line: a memory-and-succession line.

The Silver Line answers one question: what do I keep, and how does it outlive
me? It reads a declared succession picture — what is preserved, what is
entrusted to whom, what is allowed to lapse — and returns a verdict about
declared provision and review gaps. It is a method instrument. It is not an
immortality project, not an infallible archive, and never a guarantee that
anything persists.
"""

from __future__ import annotations

from .enums import IntakeDisposition, KeepKind, ProvisionStatus, VerdictStatus
from .evaluator import read_succession, read_succession_with_findings
from .intake import intake, normalize_item
from .records import (
    IntakeNote,
    ProvisionFinding,
    SuccessionItem,
    SuccessionVerdict,
)
from .registry import KEEPSAKE_TAG_VOCABULARY, SILVER_KEEPSAKES, registry_ids
from .serialization import (
    canonical_registry,
    canonical_verdict,
    registry_digest,
    verdict_digest,
)
from .version import __version__

QUESTION = "What do I keep, and how does it outlive me?"
JOB = (
    "Memory and succession: what is preserved, what is entrusted to whom, "
    "what is allowed to lapse"
)
MUST_NOT_BECOME = (
    "An immortality project, an infallible archive, or a guarantee of persistence"
)

__all__ = [
    "IntakeDisposition",
    "IntakeNote",
    "JOB",
    "KeepKind",
    "KEEPSAKE_TAG_VOCABULARY",
    "MUST_NOT_BECOME",
    "ProvisionFinding",
    "ProvisionStatus",
    "QUESTION",
    "SILVER_KEEPSAKES",
    "SuccessionItem",
    "SuccessionVerdict",
    "VerdictStatus",
    "__version__",
    "canonical_registry",
    "canonical_verdict",
    "intake",
    "normalize_item",
    "read_succession",
    "read_succession_with_findings",
    "registry_digest",
    "registry_ids",
    "verdict_digest",
]
