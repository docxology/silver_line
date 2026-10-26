# AGENTS.md — `silver_line/data/envelopes`

Prepared witness envelopes. Digests and report references must be re-derived
from the live registry and snapshots after any registry, evaluator or schema
change; `tests/test_binding_and_envelopes.py` fails on drift. This repo
prepares envelopes only — the witness register itself is never edited here.
