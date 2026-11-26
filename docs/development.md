# Development — silver_line

## Set up and verify

Run these commands from the Silver Line repository root. Install
[uv](https://docs.astral.sh/uv/) and Python 3.11 or later. The source
repository declares its development requirements in `pyproject.toml`.
Install librsvg's `rsvg-convert` for figure generation and tests
(`librsvg2-bin` on Debian or Ubuntu, `librsvg` on macOS).
`SILVER_LINE_RSVG_CONVERT` can point to an alternate executable.

```bash
uv sync
uv run pytest tests/ --cov=src --cov-report=term
uv run ruff check src tests scripts
uv run python scripts/build_figures.py
uv run python scripts/gen_formalism_ledger.py
uv run pytest tests/test_formalism_claim_ledger.py
uv run python -m silver_line.artifacts --check
uv tool run ty==0.0.90 check src
```

The native suite enforces the configured 90% coverage floor. The
[usage guide](usage.md) gives executable examples. The fixture check compares
replayed reports, snapshots, and envelope bytes with the current cohort.
Run generators in a disposable Git checkout when checking reproducibility of
tracked files.

## Invariants

1. Standalone: everything above works with zero sibling checkouts present.
2. Pure standard library at runtime; dev deps are pytest, pytest-cov, ruff.
3. No mocking framework, anywhere.
4. Fail closed: empty scan sets and unscorable registries are named outcomes.
5. Sort before emit: canonicalize sets and root scans; retain ordered nested source values.
6. Sibling line projects are never modified from here.
7. Underclaim, first person; `data/claim_ledger.yaml` is the register and
   `docs/claim_boundaries.md` its prose companion.

## Input and replay contract

The public evaluator accepts one SuccessionItem or a finite ordinary list,
tuple, set or frozenset. Arbitrary iterators are set aside without consuming
them. Custom objects with hostile iteration, property access, recursion or
unbounded content are outside this contract. No universal never-raise promise
is made. Invalid review dates and blank/noncanonical subject IDs raise
ValueError before evaluation; invalid registries return NEEDS_REWORK and keep
the supplied valid review date.
Subject configuration and registry text must contain Unicode scalar values;
valid non-ASCII text is allowed. Surrogate code units in declared content are
classified before scoring or diagnostic echo. The original-source hash uses
the explicitly versioned `silver.source/1` representation. The dedicated
`restore_source` decoder never interprets literal dictionaries as text.

Use explicit opaque item IDs for ongoing custody records. Omitted IDs receive
source-content IDs for compatibility, so changing the source changes that ID.
Duplicate usable declared IDs (even on unusable descriptions) reject the entire
scan before records are discarded. Invalid-ID diagnostic hashes do not
participate in that check. Rejected item notes preserve valid supplied IDs.
Conflicting declarations sort by ID and canonical content, so rejection
reports are deterministic too. Input
containers otherwise have scan-set semantics. Findings sort by item and
keepsake ID, notes by item/disposition/text, labels as sets. Required-evidence
tuples preserve their declared sequence, which is included in registry identity.
The review date is never the clock date, evidence freshness, or a next-review
date; `last_reviewed` remains only a declared evidence label.

Generate examples with `uv run python -m silver_line.artifacts`. Canonical
reports and original/normalized/fixture/registry snapshots are addressed by
SHA-256 under `data/reports/` and `data/snapshots/`. The builder refuses to
overwrite different bytes at an existing content address. The check mode
replays all fixtures and checks exact persisted bytes. Original and normalized
declarations are distinct snapshots; neither establishes factual custody.
For complete replay, call `restore_source` on a JSON-decoded original source
snapshot, then pass the restored native scan directly to `read_succession`.
For a retained fixture snapshot, call `restore_source` once, then pass the
restored fixture dictionary to `fixture_items`. JSON fixture admission never
decodes native nodes or historical text markers. Rejected declarations,
duplicate identity, original-source digests, counts and notes are part of the
comparison. Source decoding preserves nested container kind/order and rejected
code units without coalescing a surrogate pair into a scalar. Root scan
multisets remain order-insensitive. All emitted text must encode with strict
UTF-8. Historical snapshots require their historical producer, not an implicit
upgrade. See `tests/test_review_unicode.py` and `tests/test_source_replay.py`
for text boundaries, literal markers, nested values and complete artifact replay.
See [schema migration](report-schema.md) and [publication](publication.md).

The project has no declared type-check dependency. The pinned external ty
command above checks source without adding runtime or development dependencies.
Regression controls exercise public readings and real artifact records, not
implementation text, prose or disposable source mutations.


## Render and validate the manuscript

Install Pandoc and XeLaTeX with the
[pinned template's TeX prerequisites](https://github.com/docxology/template/blob/87704feae0a4490ef7dad9c931d268e8c30273c2/README.md#L565-L574).
Start from the Silver Line project root with the source revision committed.
The render copy uses a real Git checkout under the template's working projects
so provenance checks can read the indexed source.

```bash
silver_line_root="$(pwd)"
silver_line_revision="$(git rev-parse HEAD)"
template_root="$(mktemp -d)/template"
git clone https://github.com/docxology/template "$template_root"
git -C "$template_root" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2

render_project="$template_root/projects/working/silver_line"
mkdir -p "$template_root/projects/working"
git clone "$silver_line_root" "$render_project"
git -C "$render_project" checkout --detach "$silver_line_revision"

(
  cd "$render_project" &&
  uv sync &&
  uv run python scripts/build_figures.py
)
(
  cd "$template_root" &&
  uv sync --locked --no-dev --python 3.14 &&
  uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/silver_line &&
  uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/silver_line
)
```

The template discovers [the canonical manuscript](manuscript/README.md).
[Its configuration](manuscript/config.yaml) selects the cover, page layout,
PDF, and HTML. Inside the staged Silver Line project, inspect:

- `output/figures/` for the generated native SVG plates, cover PNG, and registry
- `output/pdf/silver_line_combined.pdf` for the typeset sections and cover
- `output/web/index.html` for the combined web manuscript
- `output/reports/validation_report.md` for the validation receipt

Tracked native figure inputs remain part of the Source archive. The ignored
PDF and web outputs are generated separately. For release evidence, follow
[the publication procedure](publication.md) and retain the provenance receipt.
