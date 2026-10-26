# AGENTS.md — `silver_line/output/figures`

Working standard for this directory.

## Gotchas

- Every file here is written by `scripts/build_figures.py` from
  `src/silver_line/figures/build.py`; hand-edits are lost on the next build.
- The cover PNG needs `rsvg-convert` on PATH (`SILVER_LINE_RSVG_CONVERT`
  overrides it); the SVGs do not.
- `figure_registry.json` is the generated index of those figures, and
  `tests/test_figures.py` gates its shape.
