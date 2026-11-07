# AGENTS.md — `silver_line/output`

Working standard for this directory. Everything here is generated: never
hand-edit a file under `output/`, and never edit one to make a check pass.

## Gotchas

- Current figures, rendered web files, and `pdf/silver_line_combined.pdf` are
  tracked. Preserve tracked outputs when regenerating current figures.
- `figures/` is reproducible from `scripts/build_figures.py`. `web/` and
  `pdf/` come from the external render pipeline (`STANDALONE.md`), not from
  this repo's scripts.
- Render provenance for a release is recorded under `docs/releases/`.
