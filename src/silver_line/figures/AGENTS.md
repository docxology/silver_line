# AGENTS.md — `silver_line/src/silver_line/figures`

Working standard for this directory.

## Gotchas

- Builders are deterministic: same registry, same bytes. A style change
  rewrites `output/figures/` and is committed together with that output.
- `figure_registry` entries are accessibility objects (`fig:` labels with
  caption and alt text); `tests/test_figures.py` gates their shape.
- `rasterize_cover` is the only subprocess here. It runs `rsvg-convert`
  (`SILVER_LINE_RSVG_CONVERT` overrides the executable) and raises
  `RuntimeError` when librsvg is missing or fails; the SVG builds themselves
  are standard library only.
