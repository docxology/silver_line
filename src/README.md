# src

`silver_line/` — the package, and the whole product surface. Pure standard
library at runtime; nothing here imports a sibling line package
(`tests/test_standalone_contract.py` gates it). `pyproject.toml` puts `src`
on pytest's `pythonpath`, so the suite imports the package without an install
step.
