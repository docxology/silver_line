"""Figure builders for the Silver Line.

Builders are pure functions over the declaration; every builder sorts before
emit and derives all content from the running package, so no number in a
figure is hand-authored.
"""

from __future__ import annotations

from .build import (
    FIGURES,
    build_all,
    build_figure,
    figure_registry,
)

__all__ = ["FIGURES", "build_all", "build_figure", "figure_registry"]
