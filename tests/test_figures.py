"""Figure builders: derived, sorted, deterministic; contract on the registry."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from silver_line.figures.build import (
    COVER_FIGURE,
    COVER_TAGLINE,
    COVER_TITLE,
    FIGURES,
    build_all,
    build_figure,
    figure_registry,
    rasterize_cover,
)


def test_at_least_three_figures_registered() -> None:
    assert len(FIGURES) >= 3


def test_build_all_writes_sorted_deterministic_svgs(tmp_path: Path) -> None:
    first = build_all(tmp_path / "a")
    second = build_all(tmp_path / "b")
    assert [p.name for p in first] == sorted(p.name for p in first)
    for p1, p2 in zip(first, second):
        assert p1.read_text() == p2.read_text()


def test_build_figure_unknown_name_raises() -> None:
    try:
        build_figure("nope", Path("."))
    except KeyError as exc:
        assert "nope" in str(exc)
    else:
        raise AssertionError("expected KeyError")


def test_figure_registry_names_builders() -> None:
    registry = figure_registry()
    assert registry
    for name, builder in registry.items():
        assert name in FIGURES
        assert builder.endswith("build_" + name.split("_", 1)[-1]) or callable(
            FIGURES[name]
        )


def test_figures_derive_from_the_declaration(tmp_path: Path) -> None:
    path = build_figure("silver_registry", tmp_path)
    text = path.read_text()
    assert "silver_line keepsake registry" in text
    assert "question-first-succession" in text


def test_cover_figure_is_registered() -> None:
    assert COVER_FIGURE in FIGURES
    assert COVER_FIGURE in figure_registry()


def test_cover_carries_only_title_and_tagline(tmp_path: Path) -> None:
    text = build_figure(COVER_FIGURE, tmp_path).read_text()
    runs = re.findall(r">([^<>]+)</text>", text)
    assert set(runs) == {COVER_TITLE, COVER_TAGLINE}
    # No dates, no version numbers, and no other text on the cover.
    joined = " ".join(runs)
    assert not re.search(r"\b20\d\d\b", joined)
    assert not re.search(r"\bv\d+\.\d+", joined)


def test_cover_rasterizes_deterministically(tmp_path: Path) -> None:
    executable = os.environ.get("SILVER_LINE_RSVG_CONVERT", "rsvg-convert")
    if shutil.which(executable) is None:
        raise AssertionError(f"{executable!r} must be on PATH to rasterize")
    first = rasterize_cover(build_figure(COVER_FIGURE, tmp_path / "a").parent)
    second = rasterize_cover(build_figure(COVER_FIGURE, tmp_path / "b").parent)
    assert first.read_bytes() == second.read_bytes()
