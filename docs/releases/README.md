# releases

Per-release records: notes for `v0.1.0` and `v0.2.0`, plus the v0.2.0 gate,
audit, artifact and rendered-provenance files. These are historical receipts;
a new release adds its own files rather than rewriting theirs.

`v0.3.0.gates.json` retains the original native preparation results separately
from the current configured PDF/HTML publication checks. The current packet was
rendered from native input `8f00a1f47a5f80916c8c73fd4944bd04d302ec90` with
template source `40b893b1c3d2741cded747a661a335ab03d4dd3b`: global references
resolve consistently, and wide math scrolls locally without page-level clipping.
`v0.3.0.artifacts.json` inventories the current source and publication
deliverables. The rendered-provenance and producer-input-rendered-provenance
files retain the genuine executed input receipt; integration does not relabel
that producer as the later source commit.

The `v0.3.0.pre-global-context.*.json` files preserve the preceding current
records byte-for-byte, including the earlier native input and template source.
Independent final audit, source publication and the author's reserve-first DOI
steps remain separate; no automated check grants custody or transfer permission.
