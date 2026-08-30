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

Rendering uses the external template checkout, not this repo. In the
template workspace, the project renders as `working/silver_line`:

```
uv run python scripts/pipeline/stage_03_render.py --project working/silver_line
```

Nothing under `/Volumes/external_drive/Git/template/projects/` is modified
by this repository.
