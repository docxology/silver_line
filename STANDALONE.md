# STANDALONE — silver_line

This repo is standalone. Run the gates below with zero sibling line
checkouts present; siblings are optional and their absence never fabricates
a value — a test that needs a sibling envelope falls back to a frozen copy
of the schema (see `tests/test_binding_and_envelopes.py`).

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py
uv run python -m silver_line.artifacts --check
```

## Rendering

Rendering uses the template engine as a build tool. Use an isolated detached
engine worktree with its exact commit recorded, and stage a separate clean
Source working copy at `projects/working/silver_line`. Select the project by
its basename so the renderer and validator agree on its combined output name;
these commands run in that worktree, not in this repository:

```
uv run python scripts/pipeline/stage_03_render.py --project silver_line
uv run python scripts/pipeline/stage_04_validate.py --project silver_line
```

The engine's active checkout is not modified. The source worktree and its
Git metadata are required for the engine's provenance checks; a plain archive
can render but cannot satisfy those checks. See docs/publication.md.

Current `output/web/` and `output/pdf/` files are disposable, git-ignored build
outputs. Generate and qualify them from the current Source before publication;
do not treat a leftover local render as current evidence. Native figure inputs
remain tracked. Preserve the original software Source, native generator and
renderer-derivative identities separately; versioned release packets under
`docs/releases/` remain historical.
