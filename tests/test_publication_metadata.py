"""CITATION.cff, config.yaml, and cross-file metadata agreement."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_citation_cff_names_version_and_license() -> None:
    text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert "version: 0.1.0" in text
    assert "license: MIT" in text


def test_config_yaml_declares_the_paper() -> None:
    text = (ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    assert "Silver Line" in text
    assert "Daniel Ari Friedman" in text


def test_package_version_matches_citation() -> None:
    from silver_line.version import __version__
    assert f"version: {__version__}" in (ROOT / "CITATION.cff").read_text()


def test_license_present() -> None:
    assert "MIT License" in (ROOT / "LICENSE").read_text()
