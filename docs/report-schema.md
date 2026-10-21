# Report schema and migration

`silver.verdict/2.0` replaces verdict schema `1.0`. The envelope field set stays
`line.report-envelope/1.0`; consumers must allow the native status
DECLARED_RELEASE and read the report's schema and qualified scope. Reports
bind original-source and normalized-declaration digests, subject and item IDs,
review date or UNDATED, evaluator/registry versions and coverage counts.

For historical verification only, `canonical_verdict_v1` preserves the exact
old field projection, JSON encoding and array ordering. Do not use it to
publish a new reading or relabel an old digest as schema 2. Old source remains
available at the pre-migration commit; old evidence is not reissued as new.

The pre-migration worked and same-subject envelopes shared one report reference
while claiming different statuses. They were inconsistent, and no retrievable
report was provided to resolve them. Both are superseded by independently
replayed synthetic fixtures. Their old bytes remain in Git history. No
factual evaluation of a sibling is implied by the same-subject example.

Each current report reference resolves to `data/reports/<report_ref>.json`.
The SHA-256 is over the exact UTF-8 file bytes (canonical JSON, no trailing
newline). Each `sha256:<digest>:<path>` source reference resolves to an exact
snapshot with that file hash. The fixture snapshot identifies the subject and
review date. The report binds its original declaration and normalized scan
digests, and the registry snapshot hash equals the report registry digest.
The fixture loader uses explicit IDs; the public API retains content-derived
IDs and UNSPECIFIED/UNDATED defaults only for compatibility.

An item's release is scoped to its exact item ID and requires a nonblank
declarer, canonical declaration date and source reference. Its date cannot be
after a supplied review date. An applicable LAPSE requirement must permit
lapse. A valid release marks applicable non-restraint findings
DECLARED_RELEASE instead of interpreting missing retention as failure.
Restraint acknowledgement remains independently required. An invalid release
produces an item-linked release-declaration gap. A release never affects
another item, proves authority, or permits any action.
