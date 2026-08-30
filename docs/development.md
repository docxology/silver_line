# Development — silver_line

## Verify commands

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term   # all green, cov >= 90
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py       # regenerate the ledger
uv run pytest tests/test_formalism_claim_ledger.py
```

## Invariants

1. Standalone: everything above works with zero sibling checkouts present.
2. Pure standard library at runtime; dev deps are pytest, pytest-cov, ruff.
3. No mocking framework, anywhere.
4. Fail closed: empty scan sets and unscorable registries are named outcomes.
5. Sort before emit: no dict/set iteration order reaches a reading or digest.
6. Sibling line projects are never modified from here.
7. Underclaim, first person; `docs/claim_boundaries.md` is the register.
