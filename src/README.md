# src

`silver_line/` — the package, and the whole product surface. Pure standard
library at runtime; no sibling checkout is read. `pyproject.toml` puts `src`
on pytest's `pythonpath`, so the suite imports the package without an install
step.
