# AGENTS.md — silver_line

## Working contract

- Standalone: installs, tests, checks, builds figures, and renders with zero
  sibling checkouts. Absence of a sibling is an outcome (`NOT_INSTALLED`),
  never an exception or a fabricated value.
- Pure standard library at runtime. Dev deps: pytest, pytest-cov, ruff.
- No mocking framework anywhere (`tests/test_no_mocks.py` enforces).
- Fail closed on empty scan sets; set aside unknown input with notes.
- Sort before emit; no iteration order reaches a reading or digest.
- Never modify sibling line projects, line_set, or witness_register. This
  repo only PREPARES `data/binding_declaration.json` and `data/envelopes/`.
- Underclaim, first person: `docs/claim_boundaries.md` is the register of
  record. Never hardcode a number or digest the code can derive.

## Verify commands

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term   # cov >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py
uv run pytest tests/test_formalism_claim_ledger.py
```

## Layout

`src/silver_line/` — version, enums, records, registry, intake, evaluator,
serialization, invariants, figures/. `tests/` — suite incl. no-mocks gate
and envelope field-set parity. `data/` — ledgers, envelopes, binding.
`manuscript/` — the line's own manuscript with `:::` formalism blocks.
