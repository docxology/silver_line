from __future__ import annotations

import json
from pathlib import Path
import re

from .registry import SILVER_KEEPSAKES
from .serialization import registry_digest

BLOCK = re.compile(r"^::: \{\.(?P<kind>[a-z]+)(?P<attrs>[^}]*)\}\s*$", re.M)
LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")


def generate(root: Path) -> int:
    formalism = root / "docs/manuscript/03b_formalism.md"
    labels = set()
    for match in BLOCK.finditer(formalism.read_text(encoding="utf-8")):
        label = LABEL.search(match.group("attrs"))
        if label:
            labels.add(label.group(1))
    if not labels:
        raise ValueError("no formalism labels; ledger generation fails closed")
    claims = [
        {
            "claim_id": "def_" + label.split(":", 1)[1].replace("-", "_"),
            "kind": "citation", "value": label,
            "source": "docs/manuscript/03b_formalism.md: definition block declared with this label",
            "source_path": "docs/manuscript/03b_formalism.md",
            "source_tier": "manuscript_formalism_block", "freshness": "active",
        } for label in sorted(labels)
    ]
    claims.append({
        "claim_id": "const_registry_digest", "kind": "constant",
        "value": registry_digest(SILVER_KEEPSAKES),
        "source": "derived at generation time from silver_line.registry.SILVER_KEEPSAKES",
        "source_path": "src/silver_line/registry.py", "source_tier": "package_constant",
        "freshness": "generated",
    })
    payload = {
        "schema_version": "1.0",
        "purpose": "Declares formalism-block labels and package constants for cross-reference resolution.",
        "boundary": "A row records a declared label or constant, not evidence that a proposition is true.",
        "claims": claims,
    }
    path = root / "data/formalism_claim_ledger.json"
    path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(root)} with {len(claims)} claims")
    return 0
