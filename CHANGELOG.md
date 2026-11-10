# Changelog

## 0.5.0 — 2026-11-09

- Remove the uncited empty references-section carrier rather than rendering
  an orphan heading and blank final page; retain bibliographic metadata and
  immutable historical publication records.
- Stop bundling unversioned current web/PDF build outputs in Source archives.
  Keep native figure inputs tracked, ignore disposable renderer outputs, and
  preserve versioned publication packets and their original provenance.
- Introduce the versioned `silver.source/1` codec through `SOURCE_CODEC`,
  `canonical_source`, and `restore_source`. Preserve supported nested native
  container kinds, dictionary keys, malformed Unicode code points, and literal
  marker-shaped dictionaries without arbitrary object loading. Root scans keep
  their order-insensitive multiset semantics.
- Keep ordinary JSON fixture admission separate from native source restoration;
  remove implicit historical-marker decoding and migrate replay callers to
  explicit restoration. Historical snapshots require their historical producer;
  accepted-only normalized snapshots still cannot replace original-source custody.
- Require arrays for ordinary JSON fixture `tags` and `evidence` before native
  label-set conversion. Refuse object keys, string characters and other
  non-array fields at fixture and artifact admission; retain malformed scalar
  label set-aside behavior inside arrays and independent release restraint.
- Detect duplicate nonempty declared scalar IDs, including rejected descriptions,
  without treating diagnostic hashes or omitted-ID defaults as declared IDs.
- Stop invariant evaluation at failed runtime registry admission and report its
  named shape failure rather than running unsafe semantic checks.
- Advance evaluator policy to `silver.evaluator/3.2`; retain registry revision
  `silver.registry/3.0`, verdict schema 3.0, and the common envelope schema.
  New source-codec bytes and dependent identities are not historical relabelings.

## 0.4.0 — 2026-11-08

- Encode malformed source text with native `silver_line.text-code-units/1`
  markers before hashing; preserve valid scalar-text canonical bytes and
  distinguish surrogate pairs from non-BMP scalars and literal escapes.
- Set aside malformed descriptions and IDs, drop malformed labels, expose
  custodian gaps and retain invalid releases as NEEDS_REWORK findings.
  Diagnostic identities are safe text; duplicate IDs still reject the whole scan.
- Decode retained original fixture and source snapshots for complete replay,
  including rejected declarations, counts, notes and original-source identity.
  Accepted-only normalized snapshots are not a general replay source.
- Advance evaluator policy to `silver.evaluator/3.1`; retain verdict schema 3.0,
  registry revision 3.0 and unchanged registry content. Historical artifacts
  remain tied to their original producers.
- Remove the incidental current-evaluator string pin from release replay
  controls; retain exact report replay and subject-scoped release assertions.
- Align current family orientation with the Line Set declaration, keeping
  Silver custody distinct from Green capacity, Copper allocation and Iron
  scenario recovery. Preserve the owner's current publication authority.
- Refresh the verified combined PDF, all HTML pages and their local assets from
  the qualified 0.4.0 producer. Add current gate and artifact packets separately
  from historical releases; publication integration does not relabel producers.

## 0.3.0 — 2026-11-06

- Emit figure registry 2.0 with canonical `alt_text`, including cover metadata.
  Preserve authored descriptions and historical artifacts; this figure metadata
  cutover does not change native verdict, evaluator, or registry revision 3.0.
- Require release declarations to name an explicit subject matching the reading
  as well as the exact item; independent restraint and lapse eligibility retain
  their native meanings. Authority and source references remain declarations.
- Reject malformed supplied fixture releases instead of erasing false-like
  values into absent release. Missing and null remain absence.
- Migrate live evidence labels to `custodian_acknowledgment` and
  `drift_acknowledgment`, with American English in maintained prose.
- Advance the native report to `silver.verdict/3.0`, evaluator revision to
  `silver.evaluator/3.0`, and registry revision to `silver.registry/3.0`
  independently of the package release. Preserve historical content addresses.
- Add subject-mismatch and malformed-loader behavioral controls; remove
  source-text, wording and incidental-output checks rather than re-pin them.
- Add a generated development dependency lock and refresh current native
  artifacts and diagrams while retaining historical release evidence.
- Exercise complete malformed declaration fields and false-like native releases,
  and replay subject-scoped release snapshots through native schema 3.0.
- Integrate the checked current PDF/HTML packet rendered with template
  `40b893b1c3d2741cded747a661a335ab03d4dd3b`, preserving global references,
  complete locally scrolling math, and genuine producer-input provenance.
  Archive the preceding current release records byte-for-byte; native evaluator,
  registry, figures, and original preparation results remain unchanged.

## 0.2.0 — 2026-10-21

- Require consistent named custody and reviewed vocabulary; distinguish
  unresolved lapse eligibility from explicit item-scoped release.
- Bind subject/item identity, review date, original and normalized declarations,
  schema/evaluator/registry versions and qualified scope into reports.
- Canonicalize scan-set output, preserve schema-1 verification, and regenerate
  distinct synthetic envelopes with retrievable reports and immutable snapshots.
- Add real-record regressions, all-field envelope controls and disposable source
  mutations; synchronize claim boundaries, formalism, figures and publication
  procedure. Runtime remains standard library only.
- Retain the last verified DOI; the new Zenodo version is Daniel's follow-up.

## 0.1.0 — 2026-08-29

- Initial release: keepsake registry, staged fail-closed intake, staged
  evaluator, deterministic digests, invariant battery, four figures,
  formalism claim ledger, witness envelopes, line_set binding declaration.
