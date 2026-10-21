# silver_line

A memory-and-succession line in the docxology line set (admitted 2026-09-01).

## What it is

The Silver Line answers one question: **what do I keep, and how does it
outlive me?** It reads a declared succession picture — what is preserved,
what is entrusted to whom, what is allowed to lapse — and returns a verdict
about declared provision and review gaps, pinned to a registry digest.

## What it is never

An immortality project. An infallible archive. A guarantee of persistence.
A KEPT verdict describes declared custody at a review date; it is never
permission and never a promise that anything survives. See
`docs/claim_boundaries.md`.

## Usage

```python
from silver_line import SuccessionItem, read_succession

verdict = read_succession(
    SuccessionItem(
        item_id="lab-notebooks",
        description="lab notebooks 2024-2026",
        custodian="a named successor",
        tags=frozenset({"record"}),
        evidence=frozenset({"succession_statement", "handoff_note"}),
    ),
    subject_id="lab-archive",
    evaluated_as_of="2026-10-20",
)
print(verdict.status)            # VerdictStatus.NEEDS_REWORK
print(verdict.registry_digest)   # pins the keepsake set used
```

An empty scan set reads `OUTSIDE_SCOPE` with intake notes; a registry that
cannot be scored fails closed as `NEEDS_REWORK`. Malformed input is set
aside with notes, never repaired into a fabricated value.

Findings identify their item and missing fields. Registry lapse eligibility
does not imply a release decision; an explicit scoped ReleaseDeclaration is
required for DECLARED_RELEASE. Restraint requirements still apply. Read
`reading_scope` and the accepted/rejected/unmatched counts alongside status.
See [report identity and migration](docs/report-schema.md).

## Verify

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py
uv run python -m silver_line.artifacts --check
uv tool run ty==0.0.90 check src
```

Renders via the external template checkout as `working/silver_line` (see
`STANDALONE.md`). Pure standard library at runtime; dev deps are pytest,
pytest-cov, and ruff.

## The Line Set

This work is one of ten in the Line Set family — eight instruments, their
cross-line reader, and the witness register that co-registers their report
envelopes without aggregation:

- [Black Line](https://github.com/docxology/black_line) — the practice registry of realized craft
- [Golden Line](https://github.com/docxology/golden_line) — the aspiration and horizon registry
- [Red Line](https://github.com/docxology/red_line) — the cognitive-security registry of self-assessments
- [White Line](https://github.com/docxology/white_line) — the absence and omission ledger
- [Violet Line](https://github.com/docxology/violet_line) — the consent ledger of affected parties
- [Blue Line](https://github.com/docxology/blue_line) — the stewardship instrument for maintained commitments
- [Green Line](https://github.com/docxology/green_line) — the capacity-under-development instrument
- [The Line Set](https://github.com/docxology/line_set) — the cross-line set reader holding instruments apart
- [The Witness Register](https://github.com/docxology/witness_register) — co-registration without aggregation
