# Maintenance record

## Workflowz review, November 10, 2026

- [x] **SL-001. Check immutable artifact regeneration.** The current
  generator recreates missing reports and snapshots from the canonical
  fixtures. Regeneration in a temporary directory restored a missing report
  and snapshot byte-for-byte. Both normal generation and `--check` rejected
  a mismatched existing report. See the
  [artifact verification commands](development.md#set-up-and-verify).
- [x] **SL-002. Align Ruff with the Python floor.**
  [`pyproject.toml`](../pyproject.toml) declares Python 3.11 as the minimum
  version and Ruff targets `py311`.
