# Examples

The worked example in `data/envelopes/silver_line_worked.json` intakes a
small lab-archive succession: one declared record with a named custodian
and a partial evidence set. Under the
[@def:keepsake] and [@def:succession-item] vocabulary, the reading returns
the [@def:verdict] status NEEDS_PROVISION: eligible lapse requirements
remain not yet declared under [@prop:lapse-gap], while the empty-registry
control fails closed under [@prop:fail-closed]. The same-subject envelope
uses a separate synthetic declaration about a witness register handoff; it
does not evaluate a live sibling. Its complete declared labels read KEPT.
Both envelopes regenerate from their named `data/fixtures/` inputs, with
distinct persisted reports and immutable snapshots. These statuses are
declaration examples, never observed custody results. Tests independently
replay them and reject altered envelope fields.
