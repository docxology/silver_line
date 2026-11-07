# Report schema and migration

`silver.verdict/3.0` is the current native report schema, replacing
`silver.verdict/2.0` for new readings. The envelope field set stays
`line.report-envelope/1.0`; consumers must allow the native status
DECLARED_RELEASE and read the report's schema and qualified scope. Reports
bind original-source and normalized-declaration digests, subject and item IDs,
review date or UNDATED, evaluator/registry revisions and coverage counts.
The native markers are `silver.evaluator/3.0` and `silver.registry/3.0`;
the distribution release is `0.3.0`, independently versioned from these contracts.

## Historical identities

For historical verification only, `canonical_verdict_v1` preserves the exact
schema-1 field projection, JSON encoding and array ordering. Do not use it to
publish a new reading or relabel an old digest with a newer schema.
Existing schema-1 and schema-2 reports and snapshots retain their exact bytes;
use their corresponding historical source to reproduce them. Old evidence
is not reissued as new.

The pre-migration worked and same-subject envelopes shared one report reference
while claiming different statuses. They were inconsistent, and no retrievable
report was provided to resolve them. Both are superseded by independently
replayed synthetic fixtures. Their old bytes remain in Git history. No
factual evaluation of a sibling is implied by the same-subject example.

## Current artifact identities

Each current report reference resolves to `data/reports/<report_ref>.json`.
The SHA-256 is over the exact UTF-8 file bytes (canonical JSON, no trailing
newline). Each `sha256:<digest>:<path>` source reference resolves to an exact
snapshot with that file hash. The fixture snapshot identifies the subject and
review date. The report binds its original declaration and normalized scan
digests, and the registry snapshot hash equals the report registry digest.
The fixture loader uses explicit IDs; the public API retains content-derived
IDs and UNSPECIFIED/UNDATED defaults only for compatibility.

Duplicate IDs are checked across the original SuccessionItem declarations,
including those whose descriptions are unusable. The whole scan is rejected
and valid declared IDs remain in rejection notes. Canonical content breaks
ID ties before digesting, so conflicting duplicate declarations have the
same rejection identity under list reversal or set input.

## Current release contract

`ReleaseDeclaration(subject_id, item_id, declared_by, declared_on, source_ref)`
requires canonical nonblank text in every field. Its subject must equal the
reading's explicit subject; `UNSPECIFIED` is not a release identity. Its item
ID must equal the exact item ID. Its canonical declaration date cannot be
after a supplied review date. An applicable LAPSE requirement must permit
lapse. Eligibility or a label alone never supplies a release decision.
A valid release marks applicable non-restraint findings DECLARED_RELEASE
instead of interpreting missing retention as failure. Restraint acknowledgment
remains independently required. An invalid declaration produces an item-linked
release-declaration gap; it cannot release another subject or item.
The declarer and source reference remain declarations, not authentication of
authority, acceptance, consent or reference contents. Release permits no action.

The fixture loader treats missing `release` and explicit JSON null as absence.
Every other supplied value must be an object with exactly the required
ReleaseDeclaration fields. Empty objects, arrays, strings, booleans, numbers,
incomplete objects and objects with extra keys raise ValueError before artifact
publication. Complete declarations with inconsistent field values remain
visible as native NEEDS_REWORK findings, never silently absent.

Replay a current normalized-declaration snapshot by passing its decoded item
array to `fixture_items({"items": snapshot})`, then calling `read_succession`
with the report's subject and review date. Canonical native bytes and the report
digest must match. Release-bearing snapshots retain all five declaration fields;
cross-subject replay and missing restraint remain NEEDS_REWORK, not permission.

## Current vocabulary and regeneration

Current labels are `custodian_acknowledgment` and `drift_acknowledgment`.
Historical records retain original British spellings, including
`custodian_acknowledgement` and `drift_acknowledgement`; these are historical
identities, not accepted aliases for current required evidence.

Regenerate the complete current fixture cohort together:

```sh
uv run python -m silver_line.artifacts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py
```

The artifact generator updates `data/envelopes/` and writes new digest-addressed
files under `data/reports/` and `data/snapshots/`; it never rewrites old addresses.
New vocabulary changes registry and declaration identities. Subject-bound release
fields change release-bearing source and declaration identities. The new schema
and revisions change current report identities. Downstream prepared consumers
must refresh from this whole cohort rather than mix old and new native records.
Regenerate current rendered output through the external renderer documented in
`STANDALONE.md`; keep archived publication receipts and rendered provenance intact.
