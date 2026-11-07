# data/AGENTS.md

`fixtures/` contains maintained synthetic declarations; `envelopes/` contains
current prepared integration inputs. Regenerate that entire cohort with
`python -m silver_line.artifacts` after registry, evaluator or schema changes.
`reports/` and `snapshots/` are immutable content-addressed stores: create new
addresses, never alter or delete historical bytes. `claim_ledger.yaml` is the
claim register of record, and `formalism_claim_ledger.json` is derived with
`scripts/gen_formalism_ledger.py`. `binding_declaration.json` is prepared input.
