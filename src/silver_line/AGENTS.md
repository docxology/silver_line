# AGENTS.md — `silver_line/src/silver_line`

Working standard for the package. The root `AGENTS.md` contract applies; this
file only narrows it.

## Gotchas

- Digests are the interface: registry, source, normalized-declaration and
  report digests are SHA-256 over canonical bytes. Changing canonicalization
  or record fields is a schema change — see `docs/report-schema.md`.
- The evaluator and intake never read the clock or the environment: the review
  date is supplied by the caller and is never a next-review date.
  `figures/build.py` is the only module that shells out (to `rsvg-convert`,
  for the cover PNG) and the only one reading an environment variable
  (`SILVER_LINE_RSVG_CONVERT`).
- `docs/claim_boundaries.md` is the register of record. A change to what the
  code can produce must be reflected there before commit.
