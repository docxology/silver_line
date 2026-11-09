# Report schema and migration

`silver.verdict/3.0` is the current native report schema, replacing
`silver.verdict/2.0` for new readings. The envelope field set stays
`line.report-envelope/1.0`; consumers must allow the native status
DECLARED_RELEASE and read the report's schema and qualified scope. Reports
bind original-source and normalized-declaration digests, subject and item IDs,
review date or UNDATED, evaluator/registry revisions and coverage counts.
The native markers are `silver.evaluator/3.2` and `silver.registry/3.0`;
the distribution is independently versioned from these contracts.
Evaluator 3.2 introduces the explicitly versioned `silver.source/1` codec,
separates source replay from JSON fixture admission, and counts duplicate usable
declared IDs rather than diagnostic hashes. Registry content and the verdict
field set do not change. Earlier reports retain their original producer
identity; current report bytes are not historical reproductions.

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

Duplicate usable declared IDs are checked across the original SuccessionItem
declarations, including those whose descriptions are unusable. A usable declared
ID is nonempty scalar text with no surrounding whitespace. The whole scan is
rejected on duplicates, and valid declared IDs remain in rejection notes.
Diagnostic `input-<hash>` identities for invalid or omitted IDs do not enter this
check; the prefix is not reserved against a real declared ID. Omitted IDs still
receive deterministic content-derived identities during evaluator preparation.
Normalized rows sort by ID and canonical content. Original root succession scans
also retain order-insensitive multiset identity across single-item, list, tuple,
set and frozenset syntax. Nested ordered values and container kinds are retained;
root scan permutation therefore does not change complete report identity.

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
load `data/snapshots/<source_digest>.json` with `json.loads`, call the public
`restore_source(snapshot)`, and pass the restored native scan directly to
`read_succession` with the report's subject, review date and exact registry.
Alternatively, call `restore_source` on the retained original fixture snapshot
and admit the resulting ordinary fixture dictionary with `fixture_items`.
`fixture_items` is JSON fixture admission: its label arrays become frozensets;
it never interprets native source nodes or historical malformed-text markers.
Complete same-policy replay retains rejected declarations and reproduces source
identity, counts, notes, status and complete canonical report bytes. Compare both
`canonical_verdict` and `verdict_digest`, not only native status.

Normalized accepted rows are a derivation snapshot, **not** a general replay
source: they cannot restore rejected declarations or original source spelling.
Even when an all-valid example replays from normalized rows, this is not proof
of complete rejected-source custody. Release-bearing snapshots retain all five
declaration fields; cross-subject replay and missing restraint remain
NEEDS_REWORK, not permission.

## Versioned native source custody

`canonical_source(raw)` emits `{"codec":"silver.source/1","value":...}` as
canonical strict-UTF-8 JSON. `restore_source` accepts only that exact envelope
version, never an unversioned historical array or a guessed upgrade.
Old issued artifacts, including evaluator 3.1's reserved
`silver_line.text-code-units/1` markers, require their historical producer.
Their bytes and identities are not rewritten.

Supported source values are ordinary None, bool, int, finite float and str,
the exact SuccessionItem and ReleaseDeclaration records, and recursively nested
ordinary list, tuple, set, frozenset and dict containers. Records and all
containers have explicit `kind`/`value` nodes. The root succession scan is a
canonically sorted `scan` multiset, decoded as a tuple; its input syntax and order
do not affect identity. Inside declarations and fixture dictionaries, lists and
tuples preserve order and kind; set/frozenset members sort canonically while
retaining kind. Dictionaries encode ordered key/value pairs recursively,
including malformed field values and keys. Literal dictionaries that resemble
codec envelopes,
record nodes or old malformed-text markers therefore remain dictionaries.
No payload-specified class is imported or loaded.

A surrogate-containing string uses a `text-code-units` node containing `ord`
values for every original Python character, in order, without stripping,
replacement or surrogate-pair folding. Scalar ASCII, accented text, non-BMP
characters, U+FFFD and literal backslash-u strings remain distinct. The new
version changes source snapshot bytes even for valid declarations; it does not
claim byte continuity with older codecs. Normalized rows remain a derived
projection; their release field uses the same typed value nodes.

Malformed codec nodes, unsupported kinds, unhashable set members/dictionary keys
and duplicate encoded keys/members raise ValueError, not silent repair.
Unsupported Python producers have only a diagnostic type identity and cannot
be replayed. Recursive, hostile or unbounded objects are outside this contract.
Original fixture snapshots use this same versioned codec, decoded once before
fixture admission; they do not reinterpret literal JSON objects as text.

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
