# Replay and migration

The current prepared inputs derive from distinct synthetic declarations in
`data/fixtures/`. Run `uv run python -m silver_line.artifacts` to regenerate,
or add `--check` to require byte-for-byte replay. Each report reference resolves
under `data/reports/`; each SHA-256 source reference resolves under
`data/snapshots/`. These examples make no claim about a live sibling.

The historical envelopes shared an inconsistent report reference. They are
superseded, with their original bytes preserved in Git history. See
`docs/report-schema.md`. The envelope field set remains unchanged; native
DECLARED_RELEASE and report schema silver.verdict/3.0 require consumer review.
Regenerate the entire current cohort together; do not mix old and new registry,
declaration or report identities. Historical snapshots and reports remain
immutable, including their original `custodian_acknowledgement` and
`drift_acknowledgement` labels. Current labels use `custodian_acknowledgment`
and `drift_acknowledgment` with no aliases.
