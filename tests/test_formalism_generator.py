import json
from pathlib import Path

import pytest

from silver_line.formalism import generate


def test_generator_uses_real_manuscript_and_fails_on_empty_labels(tmp_path):
    manuscript = tmp_path / "docs/manuscript"
    manuscript.mkdir(parents=True)
    (tmp_path / "data").mkdir()
    source = manuscript / "03b_formalism.md"
    source.write_text("::: {.definition #def:test}\ntext\n:::\n::: {.definition}\ntext\n:::\n")
    assert generate(tmp_path) == 0
    ledger = json.loads((tmp_path / "data/formalism_claim_ledger.json").read_text())
    assert ledger["claims"][0]["value"] == "def:test"
    source.write_text("no labels")
    with pytest.raises(ValueError, match="no formalism labels"):
        generate(tmp_path)


def test_generator_reproduces_tracked_ledger(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manuscript = tmp_path / "docs/manuscript"
    manuscript.mkdir(parents=True)
    (tmp_path / "data").mkdir()
    (manuscript / "03b_formalism.md").write_bytes((root / "docs/manuscript/03b_formalism.md").read_bytes())
    generate(tmp_path)
    assert (tmp_path / "data/formalism_claim_ledger.json").read_bytes() == (root / "data/formalism_claim_ledger.json").read_bytes()
