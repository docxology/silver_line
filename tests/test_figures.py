"""Figure builders: derived, sorted, deterministic; contract on the registry."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from silver_line.figures.build import (
    COVER_FIGURE,
    FIGURES,
    build_all,
    build_figure,
    figure_registry,
    rasterize_cover,
)


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


def test_figure_registry_entries_are_accessibility_objects() -> None:
    registry = figure_registry()
    figures = registry["figures"]
    assert figures
    labels = []
    for entry in figures:
        label = entry["label"]
        assert label.startswith("fig:") and label[4:]
        assert Path(entry["filename"]).stem in FIGURES
        labels.append(label)
    assert labels == sorted(labels)


def test_figure_registry_covers_every_registered_figure() -> None:
    registry = figure_registry()
    names = {Path(entry["filename"]).stem for entry in registry["figures"]}
    assert names == set(FIGURES)


def test_cover_figure_is_registered() -> None:
    assert COVER_FIGURE in FIGURES
    assert figure_registry()["cover"]["filename"] == f"{COVER_FIGURE}.png"


def test_cover_rasterizes_deterministically(tmp_path: Path) -> None:
    executable = os.environ.get("SILVER_LINE_RSVG_CONVERT", "rsvg-convert")
    if shutil.which(executable) is None:
        raise AssertionError(f"{executable!r} must be on PATH to rasterize")
    first = rasterize_cover(build_figure(COVER_FIGURE, tmp_path / "a").parent)
    second = rasterize_cover(build_figure(COVER_FIGURE, tmp_path / "b").parent)
    assert first.read_bytes() == second.read_bytes()
