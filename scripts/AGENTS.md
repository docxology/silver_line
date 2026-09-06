# AGENTS.md — `silver_line/scripts`

Working standard for this directory. The repo-wide contract is
`AGENTS.md` at the repository root; this file only narrows it for `scripts/`.

## Thin-orchestrator contract

Scripts here are orchestrators ONLY: path bootstrap (`ROOT` and `ROOT/src`
onto `sys.path`), output printing, and a delegated call into a
`src/silver_line/` entrypoint. Business, data, figure, and analysis logic
lives in `src/silver_line/`, where it is importable and covered by `tests/`.
New behavior goes in the package, never in a script. Do not add CLI surface,
config handling, or data transformations here. `scripts/README.md` carries the
user-facing inventory and must match this directory.

## Inventory

| Script | Delegates to | Writes |
|---|---|---|
| `build_figures.py` | `silver_line.figures.build`: `build_all`, `figure_registry`, `rasterize_cover` | `output/figures/*.svg`, `output/figures/silver_line_cover.png`, `output/figures/figure_registry.json` |
| `gen_formalism_ledger.py` | `silver_line.registry`: `SILVER_KEEPSAKES`; `silver_line.serialization`: `registry_digest` | `data/formalism_claim_ledger.json` |

`tests/test_standalone_contract.py` pins both filenames; renaming a script
means updating that test and both inventory tables together.

## Gotchas

- The cover rasterization shells out to `rsvg-convert` (override with
  `SILVER_LINE_RSVG_CONVERT`). Missing or broken librsvg aborts
  `build_figures.py` with a `RuntimeError` after the SVGs are written; the
  SVG builds themselves are pure standard library.
- `gen_formalism_ledger.py` overwrites `data/formalism_claim_ledger.json`
  from the live manuscript and package. Never hand-edit that file; after a
  registry or formalism-block change, regenerate, then run
  `uv run pytest tests/test_formalism_claim_ledger.py`.
- That parity test re-implements the ledger derivation independently of the
  generator on purpose. Do not collapse the two into a shared helper: the
  duplicated parsing is what keeps the drift gate from sharing a code path
  with the code it gates.
