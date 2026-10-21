# Development — silver_line

## Verify commands

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term   # all green, cov >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py       # regenerate the ledger
uv run pytest tests/test_formalism_claim_ledger.py
uv run python -m silver_line.artifacts --check
uv tool run ty==0.0.90 check src
```

## Invariants

1. Standalone: everything above works with zero sibling checkouts present.
2. Pure standard library at runtime; dev deps are pytest, pytest-cov, ruff.
3. No mocking framework, anywhere.
4. Fail closed: empty scan sets and unscorable registries are named outcomes.
5. Sort before emit: no dict/set iteration order reaches a reading or digest.
6. Sibling line projects are never modified from here.
7. Underclaim, first person; `docs/claim_boundaries.md` is the register.

## Input and replay contract

The public evaluator accepts one SuccessionItem or a finite ordinary list,
tuple, set or frozenset. Arbitrary iterators are set aside without consuming
them. Custom objects with hostile iteration, property access, recursion or
unbounded content are outside this contract. No universal never-raise promise
is made. Invalid review dates and blank/noncanonical subject IDs raise
ValueError before evaluation; invalid registries return NEEDS_REWORK and keep
the supplied valid review date.

Use explicit opaque item IDs for ongoing custody records. Omitted IDs receive
source-content IDs for compatibility, so changing the source changes that ID.
Duplicate IDs (even on unusable declarations) reject the entire scan before
records are discarded. Rejected item notes preserve valid supplied IDs.
Conflicting declarations sort by ID and canonical content, so rejection
reports are deterministic too. Input
containers otherwise have scan-set semantics. Findings sort by item and
keepsake ID, notes by item/disposition/text, labels as sets. Required-evidence
tuples preserve their declared sequence, which is included in registry identity.
The review date is never the clock date, evidence freshness, or a next-review
date; `last_reviewed` remains only a declared evidence label.

Generate examples with `uv run python -m silver_line.artifacts`. Canonical
reports and original/normalized/fixture/registry snapshots are addressed by
SHA-256 under `data/reports/` and `data/snapshots/`. The builder refuses to
overwrite different bytes at an existing content address. The check mode
replays all fixtures and checks exact persisted bytes. Original and normalized
declarations are distinct snapshots; neither establishes factual custody.
See [schema migration](report-schema.md) and [publication](publication.md).

The project has no declared type-check dependency. The pinned external ty
command above checks source without adding runtime or development dependencies.
Mutation controls run only on disposable copies under pytest's temporary root.
