# AGENTS.md — `silver_line/tests`

Working standard for this directory. Tests are the gate: never weaken, skip or
delete an assertion to make a change pass.

## Gotchas

- Standalone is the test condition. Siblings are absent by design; a test that
  needs one falls back to a frozen copy of the schema.
- Controls must be falsifiable through public behavior, native schema identity
  or real artifact validation. Do not pin implementation text or prose.
- No mocking framework anywhere. `test_no_mocks.py` enforces it.
