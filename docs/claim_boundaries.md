# Claim boundaries — silver_line

The register of record is `data/claim_ledger.yaml`. This page is the prose
companion.

## What a Silver reading claims

First person, narrow: *given this declared scan set at this review date,
against this pinned registry digest, the instrument reports which declared
evidence labels were present, which were missing, and where custodianship or
provision gaps surfaced.* A verdict describes declaration coverage. It is
reviewable because the registry is pinned and the intake is staged.

I distinguish registry permission to lapse from an item's explicit release
declaration. Missing lapse labels read NEEDS_PROVISION: eligible but not yet
declared, not a retention defect. A valid scoped `ReleaseDeclaration` supplies
the item ID, declarer, declaration date and source reference. It reads
DECLARED_RELEASE for the item, including in a mixed reading; restraint
requirements still apply. I check internal declaration consistency only.
I do not verify the declarer's authority or the referenced record.

For applicable ENTRUSTMENT requirements I require a nonblank declared custodian
as well as the required labels. A name and acknowledgement label describe
declared provision; neither establishes actual acceptance or succession.

Every finding and item note carries an item ID. Report schema
`silver.verdict/2.0` binds the subject, original-source and normalized-declaration
digests, evaluator and registry versions, review date and qualified scope.
An omitted date is explicitly UNDATED, and an omitted subject is UNSPECIFIED;
neither may be published in an envelope. I report accepted, rejected and
unmatched item counts. KEPT on a PARTIAL reading describes only its matched
accepted declarations. Unsupported or unmatched items have not been cleared.

## What a Silver reading never claims

- **Not persistence.** KEPT means declared custody was complete at the review
  date. Nothing is guaranteed to survive.
- **Not an infallible archive.** Drift is expected; the digest exists to name
  it, not to prevent it.
- **Not an immortality project.** The line's own registry contains a restraint
  keepsake (`no-infallible-archive`) refusing exactly this drift.
- **Not permission.** No verdict authorizes an action, a route, or a release.
  An explicit release declaration also gives no permission for disclosure,
  destruction or transfer, and does not establish legal authority or consent.
- **Not verified evidence.** A declared label is a declaration; the instrument
  does not check that the thing named exists or supports what it names.
- **Not a ranking.** The Silver Line does not rank, merge, or evaluate the
  other line instruments.

## Tamper-evidence and its boundary

The registry digest makes silent content edits visible. It does not make them
impossible, and it says nothing about whether the content is good. A reviewer
holding the same digest is looking at the same keepsake set; that is all.
A digest is not a confidentiality mechanism. Public examples are synthetic;
private source mappings must remain under their owner's control.
