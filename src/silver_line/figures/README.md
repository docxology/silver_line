# figures

Deterministic SVG builders for the registered figures, plus the cover plate.
`build_all` writes every registered figure into a target directory;
`scripts/build_figures.py` points it at `output/figures/` and writes
`figure_registry.json` and the cover raster alongside them.

Registry metadata schema `2.0` emits authored `alt_text` for every figure and
the cover, without an `alt` alias. Native report and evaluator identities are
unchanged; historical registries and release packets are not rewritten.
