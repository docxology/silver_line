# AGENTS.md — `silver_line/src`

Working standard for this directory. The repo-wide contract in the root
`AGENTS.md` applies in full; this file only narrows it.

## Gotchas

- Standard library only at runtime; no sibling line imports.
- Logic lives here. `scripts/` are thin orchestrators and `tests/` are the
  gate; neither is a place to put behavior.
- Emission order is a contract: findings, notes and envelope fields sort
  before they reach a reading or digest, and registry identity includes the
  declared required-evidence sequence.
- The distribution version appears in the package, `pyproject.toml`,
  `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md` and manuscript config.
  Native evaluator and registry revisions are independent markers in
  `version.py`; current envelopes carry the registry revision.
