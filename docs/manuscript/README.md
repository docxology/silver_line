# manuscript

The Silver Line's own manuscript: `00_abstract.md` through `06_conclusion.md`
and `config.yaml` (its `version` must match the package). The uncited manuscript
declares no bibliography. Root `CITATION.cff` and `CITATION.bib` retain citation
metadata for reuse without making the renderer append an empty References page.

The `:::` formalism blocks in these files are the source
of `data/formalism_claim_ledger.json`; regenerate with
`scripts/gen_formalism_ledger.py`. `MANUSCRIPT_STATUS.md` tracks publication
readiness.
