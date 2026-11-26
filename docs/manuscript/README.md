# Silver Line manuscript

This directory is the active source for *The Silver Line: A
Memory-and-Succession Instrument*. The numbered files render in this order.

1. [Abstract](00_abstract.md)
2. [Introduction](01_introduction.md)
3. [Method](02_method.md)
4. [Formalism](03b_formalism.md)
5. [Examples](04_examples.md)
6. [Limits](05_limits.md)
7. [Conclusion](06_conclusion.md)

[Configuration](config.yaml) sets the paper identity, generated cover,
geometry, and format selection. Its version must match the package.
Source citation metadata lives in [CITATION.cff](../../CITATION.cff) and
[CITATION.bib](../../CITATION.bib). The current paper is uncited and renders
without a References section.

The formalism declarations generate `data/formalism_claim_ledger.json`.
After a declaration or location change, run
`uv run python scripts/gen_formalism_ledger.py` and
`uv run pytest tests/test_formalism_claim_ledger.py` from the project root.

See the [pinned render workflow](../development.md#render-and-validate-the-manuscript)
and the [manuscript status](MANUSCRIPT_STATUS.md).
