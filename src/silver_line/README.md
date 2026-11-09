# silver_line

The package. `__init__` re-exports the public surface: records and enums,
`intake`/`normalize_item`, `read_succession`, `read_succession_with_findings`,
the registry (`SILVER_KEEPSAKES`, `KEEPSAKE_TAG_VOCABULARY`, `registry_ids`),
canonical serialization and digests, `SOURCE_CODEC`, `canonical_source`,
`restore_source`, and `__version__`.
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
| `snapshots.py` | canonical JSON/source digests, item snapshots, versioned native source codec |
| `invariants.py` | offline invariant battery over the line's own declaration |
| `artifacts.py` | JSON fixture admission and `python -m silver_line.artifacts [--check]` builder |
| `formalism.py` | derives `data/formalism_claim_ledger.json` |
| `figures/` | deterministic SVG builders and the cover raster |

Commands and invariants: `docs/development.md`.
`silver.source/1` preserves native nested container kinds, ordered values,
literal dictionaries and rejected Unicode code units. Root succession scans
retain canonical order-insensitive multiset identity. `restore_source` decodes
the versioned original-source snapshot to a native scan for evaluation.
For a held original fixture snapshot, decode once with `restore_source` and then
call `fixture_items` on the restored fixture dictionary. `fixture_items` itself
admits ordinary JSON arrays as frozen label sets; it never decodes native nodes.
Normalized accepted rows are not complete replay sources; see
`docs/report-schema.md`. Earlier snapshots require their historical producer.
