# data/AGENTS.md

Everything in this directory is either derived (formalism_claim_ledger.json —
regenerate with scripts/gen_formalism_ledger.py) or a prepared integration
input (binding_declaration.json, envelopes/). Envelope digests must be
re-derived from the live registry after any registry edit; a stale digest is
drift, and tests/test_binding_and_envelopes.py fails on it.
