"""Figure builders: derived, sorted, deterministic; contract on the registry."""

from __future__ import annotations

from pathlib import Path

from silver_line.figures.build import (
    FIGURES,
    build_all,
    build_figure,
    figure_registry,
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
