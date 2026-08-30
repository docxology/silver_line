"""The standalone contract: documented verify commands match declared dev deps."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_dev_deps_cover_the_documented_contract() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for dep in ("pytest", "pytest-cov", "ruff"):
        assert dep in pyproject


def test_documented_commands_exist() -> None:
    for script in ("build_figures.py", "gen_formalism_ledger.py"):
        assert (ROOT / "scripts" / script).exists()


def test_no_sibling_imports_in_src() -> None:
    """Zero siblings present is the test condition; src must not import them."""
    forbidden = ("black_line", "golden_line", "white_line", "red_line",
                 "line_set", "witness_register")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in forbidden:
            assert name not in text, f"{path.name} imports {name}"
