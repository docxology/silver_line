# AGENTS.md — `silver_line/tests`

Working standard for this directory. Tests are the gate: never weaken, skip or
delete an assertion to make a change pass.

## Gotchas

- Standalone is the test condition. Siblings are absent by design; a test that
  needs one falls back to a frozen copy of the schema.
- Controls must be able to fail. `test_review_mutation_controls.py` mutates
  disposable copies under pytest's temporary root; keep new controls equally
  falsifiable.
- `test_standalone_contract.py` pins the two `scripts/` filenames, checks the
  documented dev dependencies are declared in `pyproject.toml`, and fails if
  `src/` names a sibling line package.
- No mocking framework anywhere. `test_no_mocks.py` enforces it.
