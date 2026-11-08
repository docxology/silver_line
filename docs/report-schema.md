# Report schema and migration

`silver.verdict/3.0` is the current native report schema, replacing
`silver.verdict/2.0` for new readings. The envelope field set stays
`line.report-envelope/1.0`; consumers must allow the native status
DECLARED_RELEASE and read the report's schema and qualified scope. Reports
bind original-source and normalized-declaration digests, subject and item IDs,
review date or UNDATED, evaluator/registry revisions and coverage counts.
The native markers are `silver.evaluator/3.1` and `silver.registry/3.0`;
the distribution release is `0.4.0`, independently versioned from these contracts.
Evaluator 3.1 adds the malformed-source policy below without changing registry
content or the verdict field set. Evaluator 3.0 reports retain their original
producer identity; current report bytes are not historical reproductions.

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

Replay a complete current reading from the retained **original-source** snapshot:
load `data/snapshots/<source_digest>.json` with `json.loads`, pass that item
array to `fixture_items({"items": snapshot})`, and call `read_succession` with
the report's subject, review date and exact registry. Alternatively, decode
the retained original fixture snapshot and use its subject and review date.
`fixture_items` decodes native malformed-text markers before constructing
declarations. Both paths retain rejected declarations and reproduce original
source identity, rejection counts, notes and complete canonical report bytes.
Compare both `canonical_verdict` and `verdict_digest`, not only native status.

Normalized accepted rows are a derivation snapshot, **not** a general replay
source: they cannot restore rejected declarations or original source spelling.
Even when an all-valid example replays from normalized rows, this is not proof
of complete rejected-source custody. Release-bearing snapshots retain all five
declaration fields; cross-subject replay and missing restraint remain
NEEDS_REWORK, not permission.

## Malformed-text custody policy

Native `silver_line.text-code-units/1` is an additive snapshot text codec.
Only a string containing a surrogate code point becomes an object of the form
`{"silver_line.text-code-units/1":[55296]}`. The integer array contains `ord`
values for **every** original Python character, in order, without stripping,
replacement or surrogate-pair folding. The decoder validates its reserved
single-key object, integer ranges and presence of a surrogate. This marker is
reserved for text fields in native snapshots, not an arbitrary JSON-object
interchange format. Unsupported Python producers remain outside the contract.
Malformed snapshot markers raise ValueError; they are never silently repaired.

Valid ASCII, accented text, non-BMP scalars, U+FFFD and literal backslash-u
strings retain their existing canonical UTF-8 bytes. A two-surrogate Python
string stays distinct from its corresponding non-BMP scalar after JSON decode.
Source collection sorting remains unchanged; fixture arrays retain their order.
Original fixture and declaration snapshots both use this encoding, and
`fixture_items` is the existing decode/replay consumer for both. Digests bind
the safe canonical representation; surrogatepass is not used as UTF-8 output.

Malformed descriptions and IDs reject their declarations; valid declared IDs
remain available for whole-scan duplicate checks even on rejected descriptions.
Invalid IDs receive deterministic safe source-content diagnostic identities.
Malformed custodians become explicit custody gaps, malformed labels are dropped
with notes, and malformed release fields remain present and produce a
release-declaration NEEDS_REWORK finding, never absence or a successful release.
Subject configuration must be scalar canonical text; unsafe registries fail
closed before hashing or diagnostic echo. Valid non-ASCII text remains allowed.
Canonical reports, source/fixture/normalized snapshots and artifact files are
strict UTF-8; this codec changes neither the family envelope format nor siblings.

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
