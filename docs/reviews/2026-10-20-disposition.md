# Review implementation disposition

Review source: the LineSet email received 2026-10-21, copied verbatim into
`Local/lineset-review-packets-20261021/silver_line.review.md` on GitVault.
Body SHA-256: `433af116b835b7deafa31fc9fcbf24fc72dd539453915d23f3f85b302ef4ff1b`.
Reviewed base: `c66ccb46fe32aea4ba3ac03b149403b1a33bc1fb`.

The initial baseline ran 74 tests at 97.65% coverage. Before implementation,
the added review regressions produced **18 failed, 1 passed**. The passing
case was a valid custodian without acknowledgement: the original evaluator
already reported that gap, so that branch was retained. The failing cases
reproduced all eight numbered findings. Full failure output is retained in
the release run directory on GitVault and accompanies the release evidence.

| Item | Disposition | Implementation and acceptance evidence |
|---|---|---|
| SL-01 | Done | Applicable entrustment requires a named custodian; structured missing fields and item IDs; blank/whitespace/nontext variants and unrelated complete-item control in test_review_boundaries and test_review_acceptance. |
| SL-02 | Done; extension option adapted | Runtime registry validation rejects unknown tags and intake actually filters them. Small custom registries remain supported. Arbitrary versioned vocabulary inputs are deliberately not added; extending vocabulary requires a reviewed package revision, preserving the narrow runtime contract. |
| SL-03 | Done | Eligibility reads not-yet-declared NEEDS_PROVISION. Explicit item-scoped release includes declarer/date/source; DECLARED_RELEASE carries no retention penalty and never waives restraint. Invalid/future/mismatched/unscoped declarations fail closed. No permission or verified authority claim. |
| SL-04 | Done | Explicit subject/item IDs, linked findings/notes, original and normalized digests, evaluator/schema identity, duplicate rejection, controlled content-derived compatibility IDs, retrievable reports and snapshots. |
| SL-05 | Done | Both public APIs accept explicit dates; valid dates survive empty and invalid-registry branches. Invalid dates raise documented ValueError. Omitted dates read UNDATED; publication requires dated, identified reports. |
| SL-06 | Done | Scan-set and registry permutations sort before emission; actual set inputs agree across three hash seeds. Required-evidence sequence remains part of registry identity. Duplicate IDs reject the scan. |
| SL-07 | Done | Distinct canonical synthetic fixtures drive status, report reference, subject/date, registry/version and immutable snapshots. Content-addressed reports are retrievable. Every envelope field is independently altered and removed to prove rejection. Historical inconsistent examples are superseded, not relabelled. |
| SL-08 | Done | Removed the vacuous assertion and self-comparison. Real-record regressions, permutation tests, exact file replay, all-field controls and four disposable source mutations verify that the checks can reject defects. Claim ledger links semantic claims to behavioral tests and keeps formalism parity separate from proof. |
| P2 registry shape | Done | Explicit KeepKind membership, canonical unique evidence labels, reviewed tag vocabulary, LAPSE-only eligibility; shared runtime validation also appears in offline invariants. |
| P2 scope loss | Done | Accepted/rejected/unmatched counts and COMPLETE/PARTIAL/EMPTY/UNSCORABLE scope. A favorable partial reading does not clear rejected or unmatched items. Unknown tags do not automatically become custody defects. |
| P2 input boundary | Adapted as proposed | Finite ordinary containers are supported; arbitrary iterators are set aside without consumption. Hostile/unbounded Python objects are outside the documented boundary, avoiding a false never-raise promise. |
| Delivery refactors | Done | Frozen records and standard-library runtime retained. Formalism generator moved into the package under the existing thin-script contract; independent parity parsing remains in tests. Figure callable typing corrected after an executed type-check failure. |
| Publication procedure | Adapted to missing file | docs/publication.md did not exist at base. Added the brief's reserve-first, isolated-engine, audited, leased source-release procedure without inventing a DOI. |

The implementation is one synchronized change because boundary semantics,
report identity, fixtures, generated envelopes and manuscript claims must
agree before commit. The versioned release metadata is a subsequent commit.
The release packet identifies both commits and records final-tree gates.

Rendering adaptation: the archive attempt rendered but could not bind the
engine's Git-backed provenance. The release uses the permitted detached
origin/main worktree instead. The validator then correctly rejected final
outputs hidden by per-format ignore rules. Final PDF/HTML and local web
assets are now published; intermediates remain ignored. Engine code was
not changed, no check was skipped, and no threshold was lowered.

Cross-repository finding: consumers of native statuses must recognize
DECLARED_RELEASE and inspect the schema-2 report and qualified reading scope.
The envelope field set remains unchanged. Sibling same-subject examples may
need their own immutable fixtures/replay checks; this run makes no claim that
they were audited. No sibling repository was changed.

Scientific boundary: all examples are synthetic declaration checks. No new
empirical result, verified acceptance, succession right, consent, persistence,
permission or cross-line compensation is claimed.

## Independent audit corrections

The first independent audit requested changes to SL-04, SL-06 and SL-08.
An unusable declaration could disappear before duplicate-ID enforcement,
and conflicting duplicate declarations retained input order in the normalized
digest. New regressions first failed with **2 failed, 22 deselected**.
The correction checks IDs before discarding unusable records, preserves valid
declared IDs in rejection notes, and sorts content as the tie-breaker for
duplicate IDs. Reversed lists and real set inputs now agree. The release
packet records the correction commit and the second independent audit.
