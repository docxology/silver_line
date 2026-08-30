"""Generate data/formalism_claim_ledger.json from the manuscript and package.

Every row is derived, never hand-authored: citation rows from the
``::: {.definition #def:...}`` blocks declared in the manuscript, constant
rows from the running package. Tests re-derive the whole set and fail on
drift.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript"
FORMALISM = MANUSCRIPT / "03b_formalism.md"
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

_BLOCK = re.compile(r"^::: \{\.(?P<kind>[a-z]+)(?P<attrs>[^}]*)\}\s*$", re.M)
_LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")
_REFERENCE = re.compile(
    r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]"
)


def declared_labels() -> set[str]:
    labels: set[str] = set()
    for match in _BLOCK.finditer(FORMALISM.read_text(encoding="utf-8")):
        label = _LABEL.search(match.group("attrs"))
        if label:
            labels.add(label.group(1))
    return labels


def referenced_labels() -> set[str]:
    refs: set[str] = set()
    for path in sorted(MANUSCRIPT.glob("*.md")):
        if path.name == "preamble.md":
            continue
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from silver_line.registry import SILVER_KEEPSAKES
    from silver_line.serialization import registry_digest

    claims: list[dict[str, str]] = []
    for label in sorted(declared_labels()):
        claims.append(
            {
                "claim_id": "def_" + label.split(":", 1)[1].replace("-", "_"),
                "kind": "citation",
                "value": label,
                "source": "manuscript/03b_formalism.md: definition block declared with this label",
                "source_path": "manuscript/03b_formalism.md",
                "source_tier": "manuscript_formalism_block",
                "freshness": "active",
            }
        )
    claims.append(
        {
            "claim_id": "const_registry_digest",
            "kind": "constant",
            "value": registry_digest(SILVER_KEEPSAKES),
            "source": "derived at generation time from silver_line.registry.SILVER_KEEPSAKES",
            "source_path": "src/silver_line/registry.py",
            "source_tier": "package_constant",
            "freshness": "generated",
        }
    )
    payload = {
        "schema_version": "1.0",
        "purpose": (
            "Declares the manuscript's formalism-block labels and the package "
            "constants the formalism section states, so the render engine's "
            "evidence registry can resolve the cross-references."
        ),
        "boundary": (
            "A row here records that a label is declared and that a constant "
            "exists. It is not evidence that the proposition it names is true."
        ),
        "claims": claims,
    }
    LEDGER.write_text(
        json.dumps(payload, indent=1, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {LEDGER.relative_to(ROOT)} with {len(claims)} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
