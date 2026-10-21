# STANDALONE — silver_line

This repo is standalone. Every gate below passes with zero sibling line
checkouts present; siblings are optional and their absence never fabricates
a value — a test that needs a sibling envelope falls back to a frozen copy
of the schema (see `tests/test_binding_and_envelopes.py`).

```
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
```

## Rendering

Rendering uses the template engine as a build tool. Use an isolated detached
worktree of its origin/main, and link this repository at
`projects/working/silver_line` in that worktree. Select the project by its
basename so the renderer and validator agree on its combined output name:

```
uv run python scripts/pipeline/stage_03_render.py --project silver_line
uv run python scripts/pipeline/stage_04_validate.py --project silver_line
```

The engine's active checkout is not modified. The source worktree and its
Git metadata are required for the engine's provenance checks; a plain archive
can render but cannot satisfy those checks. See docs/publication.md.
