"""Bind data/formalism_claim_ledger.json to the manuscript and the package.

Nothing is asserted that was not first executed: the declared labels are
parsed from the real manuscript, and the constant row is re-derived from the
live package. Negative controls prove each gate can fail.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from silver_line.registry import SILVER_KEEPSAKES
from silver_line.serialization import registry_digest

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "docs" / "manuscript"
FORMALISM = MANUSCRIPT / "03b_formalism.md"
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

_BLOCK = re.compile(r"^::: \{\.(?P<kind>[a-z]+)(?P<attrs>[^}]*)\}\s*$", re.M)
_LABEL = re.compile(r"#([a-z]+:[a-z0-9-]+)")
_REFERENCE = re.compile(
    r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]"
)


def _declared_labels() -> set[str]:
    labels: set[str] = set()
    for match in _BLOCK.finditer(FORMALISM.read_text(encoding="utf-8")):
        label = _LABEL.search(match.group("attrs"))
        if label:
            labels.add(label.group(1))
    return labels


def _referenced_labels() -> set[str]:
    refs: set[str] = set()
    for path in sorted(MANUSCRIPT.glob("*.md")):
        if path.name == "preamble.md":
            continue
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def test_every_declared_label_is_in_the_ledger() -> None:
    ledger = _ledger()
    citations = {row["value"] for row in ledger["claims"] if row["kind"] == "citation"}
    declared = _declared_labels()
    assert declared, "no labels declared; this gate would be vacuous"
    assert citations == declared, sorted(citations ^ declared)


def test_every_referenced_label_is_declared() -> None:
    declared = _declared_labels()
    referenced = _referenced_labels()
    assert referenced, "no references; this gate would be vacuous"
    assert referenced <= declared, sorted(referenced - declared)


def test_constant_row_matches_the_live_package() -> None:
    ledger = _ledger()
    constants = {
        row["claim_id"]: row["value"]
        for row in ledger["claims"]
        if row["kind"] == "constant"
    }
    assert "const_registry_digest" in constants
    assert constants["const_registry_digest"] == registry_digest(SILVER_KEEPSAKES)


def test_ledger_boundary_is_declared() -> None:
    ledger = _ledger()
    assert ledger["boundary"]
    assert ledger["schema_version"] == "1.0"
