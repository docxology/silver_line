# AGENTS.md — `silver_line/output`

Working standard for this directory. Everything here is generated: never
hand-edit a file under `output/`, and never edit one to make a check pass.

## Gotchas

- Native figures remain tracked. Preserve their source-bound identity when
  regenerating them with `scripts/build_figures.py`.
- `web/` and `pdf/` are disposable, git-ignored build outputs from the external
  render pipeline (`STANDALONE.md`), not tracked current publication authority.
  Regenerate them from qualified current Source instead of bundling stale
  pages or editing generated files.
- Versioned release packets and their original render provenance remain under
  `docs/releases/`; this cutover does not rewrite those historical bytes.
