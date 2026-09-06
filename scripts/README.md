# scripts

Thin orchestrators only: path bootstrap plus a delegated call into a
`src/silver_line/` entrypoint. All figure, registry, and derivation logic
lives in the package, where it is importable and testable. The thin-orchestrator
contract for this directory is stated in `AGENTS.md`.

## Inventory

| Script | Purpose | Delegates to | Run command |
|---|---|---|---|
| `build_figures.py` | Build every registered figure (SVG plus cover PNG) into `output/figures/` and write `figure_registry.json` | `silver_line.figures.build`: `build_all`, `figure_registry`, `rasterize_cover` | `uv run python scripts/build_figures.py` |
| `gen_formalism_ledger.py` | Derive `data/formalism_claim_ledger.json` from the manuscript's `:::` formalism blocks and the live package constants | `silver_line.registry`: `SILVER_KEEPSAKES`; `silver_line.serialization`: `registry_digest` | `uv run python scripts/gen_formalism_ledger.py` |

## Outputs

- `build_figures.py` → `output/figures/*.svg`, `output/figures/silver_line_cover.png`,
  `output/figures/figure_registry.json`
- `gen_formalism_ledger.py` → `data/formalism_claim_ledger.json` (generated; never hand-edit)

Adding a script: keep it a thin orchestrator (see `AGENTS.md`), then add a row
to the inventory table here and in `AGENTS.md`.
