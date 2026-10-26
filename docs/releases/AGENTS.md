# AGENTS.md — `silver_line/docs/releases`

Working standard for this directory.

## Gotchas

- Release records are receipts: the commands, exit codes and outputs as they
  ran. Never edit a past release's bytes, and never "fix" a recorded failure.
- A new release's gate file should name the verify commands from the root
  `AGENTS.md` list, so the two can be compared.
- Version strings recorded here must match `silver_line.version.__version__`.
