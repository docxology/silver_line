"""Version authority and derived-artifact freshness."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_version_matches_version_module() -> None:
    from silver_line.version import __version__
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{__version__}"' in pyproject


def test_registry_version_in_envelopes_matches() -> None:
    from silver_line.version import __version__
    for name in ("silver_line_worked.json", "silver_line_same_subject.json"):
        envelope = json.loads(
            (ROOT / "data" / "envelopes" / name).read_text(encoding="utf-8")
        )
        assert envelope["registry_version"] == __version__


def test_changelog_names_current_version() -> None:
    from silver_line.version import __version__
    assert f"## {__version__}" in (ROOT / "CHANGELOG.md").read_text()


def test_all_active_publication_versions_agree() -> None:
    from silver_line.version import __version__
    assert json.loads((ROOT / ".zenodo.json").read_text())["version"] == __version__
    config = (ROOT / "docs/manuscript/config.yaml").read_text()
    assert re.search(r'^  version: "([^"]+)"$', config, re.M).group(1) == __version__
