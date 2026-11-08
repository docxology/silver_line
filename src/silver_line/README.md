# silver_line

The package. `__init__` re-exports the public surface: records and enums,
`intake`/`normalize_item`, `read_succession`, `read_succession_with_findings`,
the registry (`SILVER_KEEPSAKES`, `KEEPSAKE_TAG_VOCABULARY`, `registry_ids`),
canonical serialization and digests, and `__version__`.
Native revisions live in `version.py` as `EVALUATOR_REVISION` and
`REGISTRY_REVISION`, independently of the distribution version.

| Module | Role |
|---|---|
| `version.py` | version markers |
| `enums.py` | `ProvisionStatus`, `VerdictStatus`, `KeepKind`, `IntakeDisposition` |
| `records.py` | frozen records: `Keepsake`, `SuccessionItem`, `IntakeNote`, `ProvisionFinding`, `SuccessionVerdict`, `ReleaseDeclaration` |
| `registry.py` | the versioned keepsake registry and its tag vocabulary |
| `intake.py` | normalization, label cleaning, vocabulary and shape checks |
| `evaluator.py` | `read_succession`, `read_succession_with_findings` |
| `validation.py` | review-date and registry-shape validation |
| `serialization.py` | canonical registry and verdict bytes, plus digests |
| `snapshots.py` | canonical JSON/source digests, item snapshots, native malformed-text codec |
| `invariants.py` | offline invariant battery over the line's own declaration |
| `artifacts.py` | original fixture/source snapshot decode and `python -m silver_line.artifacts [--check]` builder |
| `formalism.py` | derives `data/formalism_claim_ledger.json` |
| `figures/` | deterministic SVG builders and the cover raster |

Commands and invariants: `docs/development.md`.
`silver_line.text-code-units/1` encodes only surrogate-containing strings;
valid text bytes are unchanged. `fixture_items` restores retained rejected
declarations before evaluation. Complete replay requires original source or
fixture snapshots, not only accepted normalized rows; see `docs/report-schema.md`.
