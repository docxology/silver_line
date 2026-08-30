# Extending the Silver Line

## Adding a keepsake

Append one `Keepsake` to `SILVER_KEEPSAKES` in `src/silver_line/registry.py`.
Constraints, each enforced by the invariant battery or the evaluator:

| Field | Constraint | Check |
| --- | --- | --- |
| `id` | Unique across the registry. | `check_unique_keepsake_ids` |
| `tags` | Subset of `KEEPSAKE_TAG_VOCABULARY`. | `check_tags_in_vocabulary` |
| `required_evidence` | Non-empty, non-blank labels. | evaluator shape check |
| `kind` | A `KeepKind` member. | evaluator shape check |
| `may_lapse` | Boolean. | evaluator shape check |

After any registry edit, regenerate the formalism ledger and re-derive both
envelope digests — tests fail until the derived artifacts follow.

## Adding a keep kind

Extend `KeepKind`, add at least one keepsake of the new kind (the
`lapse_families_present` invariant fails closed on a missing family), and add
the tag vocabulary the kind needs.

## What this file does not claim

That extending the line is cheap. The bookkeeping is one edit; the instrument
is the part that has to be worth keeping.
