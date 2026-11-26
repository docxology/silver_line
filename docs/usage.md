# Silver Line usage

Follow the [development setup](development.md) and run these examples with
`uv run python` from the project root. All declarations below are synthetic.

## Read a succession declaration

```python
from silver_line import SuccessionItem, read_succession

verdict = read_succession(
    SuccessionItem(
        item_id="lab-notebooks",
        description="lab notebooks 2024-2026",
        custodian="a named successor",
        tags=frozenset({"record"}),
        evidence=frozenset({"succession_statement", "handoff_note"}),
    ),
    subject_id="lab-archive",
    evaluated_as_of="2026-10-20",
)
print(verdict.status)            # VerdictStatus.NEEDS_REWORK
print(verdict.registry_digest)   # pins the keepsake set used
```

An empty scan set reads `OUTSIDE_SCOPE` with intake notes; a registry that
cannot be scored fails closed as `NEEDS_REWORK`. Malformed input is set
aside with notes, never repaired into a fabricated value.
Malformed Unicode code units, nested container kinds, ordered values and literal
dictionaries are retained in versioned `silver.source/1` snapshots. Complete
same-policy replay uses `restore_source` on original snapshots, not JSON fixture
admission or accepted normalized rows. Root scan identity remains order-insensitive;
historical artifacts require their historical producer.

Findings identify their item and missing fields. Registry lapse eligibility
does not imply a release decision; DECLARED_RELEASE requires a declaration
matching both the explicit reading subject and the exact item ID. Restraint
requirements still apply. For example:

```python
from silver_line import ReleaseDeclaration, SuccessionItem, read_succession

item = SuccessionItem(
    item_id="retired-index",
    description="Synthetic retired index",
    tags=frozenset({"record"}),
    evidence=frozenset({"drift_acknowledgment"}),
    release=ReleaseDeclaration(
        subject_id="archive-a", item_id="retired-index",
        declared_by="declared successor role", declared_on="2026-10-19",
        source_ref="synthetic:release-record",
    ),
)
matching = read_succession(item, subject_id="archive-a", evaluated_as_of="2026-10-20")
mismatched = read_succession(item, subject_id="archive-b", evaluated_as_of="2026-10-20")
assert matching.status.value == "DECLARED_RELEASE"
assert mismatched.status.value == "NEEDS_REWORK"
```

These fields are declarations, not authentication of authority, source
contents, acceptance or consent. Release authorizes no action.
Read `reading_scope` and the accepted/rejected/unmatched counts alongside status.
See [report identity and migration](report-schema.md).

## Retain and replay the source

Keep the review date, explicit subject, registry identity and original-source
snapshot with a verdict that needs replay. The [report schema](report-schema.md)
describes original-source restoration, normalization, and historical producer
requirements. An envelope is a structural pointer for co-registration. Only
export a dated reading with an explicit subject and follow the
[claim boundaries](claim_boundaries.md) when interpreting the result.
