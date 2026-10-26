# AGENTS.md — `silver_line/src`

Working standard for this directory. The repo-wide contract in the root
`AGENTS.md` applies in full; this file only narrows it.

## Gotchas

- Standard library only at runtime. `tests/test_standalone_contract.py` fails
  if `src/` names a sibling line package.
- Logic lives here. `scripts/` are thin orchestrators and `tests/` are the
  gate; neither is a place to put behavior.
- Emission order is a contract: findings, notes and envelope fields sort
  before they reach a reading or digest, and registry identity includes the
  declared required-evidence sequence.
- The version appears in several places (this package, `pyproject.toml`,
  `CITATION.cff`, `.zenodo.json`, `CHANGELOG.md`, `docs/manuscript/config.yaml`
  and the envelopes). `tests/test_version_sync.py` gates the ones it reads.
