# silver_line

A memory-and-succession line: the fifth colour in the docxology line set.

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
        description="lab notebooks 2024-2026",
        custodian="a named successor",
        tags=frozenset({"record"}),
        evidence=frozenset({"succession_statement", "handoff_note"}),
    )
)
print(verdict.status)            # VerdictStatus.NEEDS_REWORK
print(verdict.registry_digest)   # pins the keepsake set used
```

An empty scan set reads `OUTSIDE_SCOPE` with intake notes; a registry that
cannot be scored fails closed as `NEEDS_REWORK`. Malformed input is set
aside with notes, never repaired into a fabricated value.

## Verify

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
```

Renders via the external template checkout as `working/silver_line` (see
`STANDALONE.md`). Pure standard library at runtime; dev deps are pytest,
pytest-cov, and ruff.
