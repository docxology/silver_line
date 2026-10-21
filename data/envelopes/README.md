# Replay and migration

The current prepared inputs derive from distinct synthetic declarations in
`data/fixtures/`. Run `uv run python -m silver_line.artifacts` to regenerate,
or add `--check` to require byte-for-byte replay. Each report reference resolves
under `data/reports/`; each SHA-256 source reference resolves under
`data/snapshots/`. These examples make no claim about a live sibling.

The historical envelopes shared an inconsistent report reference. They are
superseded, with their original bytes preserved in Git history. See
`docs/report-schema.md`. The envelope field set remains unchanged; native
DECLARED_RELEASE and report schema silver.verdict/2.0 require consumer review.
