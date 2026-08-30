"""The figure registry and deterministic SVG figure builders.

Every builder derives its content from the live keepsake registry, sorts
every emitted sequence, and writes deterministic SVG. A figure is a reading
aid, not evidence; captions in the manuscript say what each one does and
does not show.
"""

from __future__ import annotations

from pathlib import Path

from ..enums import KeepKind
from ..registry import KEEPSAKE_TAG_VOCABULARY, SILVER_KEEPSAKES
from ..records import Keepsake


def _keepsake_rows(
    keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES,
) -> list[tuple[str, str, str, bool]]:
    """One sorted row per keepsake: id, kind, evidence count, may-lapse."""

    return sorted(
        (
            keepsake.id,
            keepsake.kind.value,
            str(len(keepsake.required_evidence)),
            keepsake.may_lapse,
        )
        for keepsake in keepsakes
    )


def _svg(title: str, rows: list[str]) -> str:
    """Render a minimal deterministic SVG list figure."""

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" '
        f'height="{40 * (len(rows) + 2)}">',
        f"<title>{title}</title>",
        f'<text x="16" y="24" font-family="monospace" font-size="14">{title}</text>',
    ]
    for index, row in enumerate(rows):
        lines.append(
            f'<text x="24" y="{52 + 40 * index}" font-family="monospace" '
            f'font-size="12">{row}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def build_registry_figure(keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES) -> str:
    """The keepsake roster, one sorted row per entry."""

    rows = [
        f"{keepsake_id} | {kind} | evidence={evidence} | may_lapse={may_lapse}"
        for keepsake_id, kind, evidence, may_lapse in _keepsake_rows(keepsakes)
    ]
    return _svg("silver_line keepsake registry", rows)


def build_family_figure(keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES) -> str:
    """Keep-kind balance: the registry reviewed for succession-family coverage."""

    counts = {kind.value: 0 for kind in KeepKind}
    for keepsake in keepsakes:
        counts[keepsake.kind.value] += 1
    rows = [f"{kind}: {counts[kind]}" for kind in sorted(counts)]
    return _svg("silver_line keep-kind balance", rows)


def build_evidence_figure(keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES) -> str:
    """The evidence-label surface a successor could inspect, per keepsake."""

    rows = sorted(
        f"{keepsake.id}: " + ", ".join(sorted(keepsake.required_evidence))
        for keepsake in keepsakes
    )
    return _svg("silver_line required evidence labels", rows)


def build_vocabulary_figure(
    keepsakes: tuple[Keepsake, ...] = SILVER_KEEPSAKES,
) -> str:
    """The reviewed tag vocabulary next to what the declaration actually uses."""

    used: set[str] = set()
    for keepsake in keepsakes:
        used |= keepsake.tags
    rows = sorted(
        f"{tag}: {'used' if tag in used else 'unused'}"
        for tag in KEEPSAKE_TAG_VOCABULARY
    )
    return _svg("silver_line tag vocabulary", rows)


#: The figure registry. Emission is sorted by name.
FIGURES: dict[str, object] = {
    "silver_registry": build_registry_figure,
    "silver_family_balance": build_family_figure,
    "silver_evidence_labels": build_evidence_figure,
    "silver_tag_vocabulary": build_vocabulary_figure,
}


def figure_registry() -> dict[str, str]:
    """Return the figure registry as a JSON-able mapping of name to builder name."""

    return {
        name: getattr(builder, "__name__", str(builder))
        for name, builder in sorted(FIGURES.items())
    }


def build_figure(name: str, output_dir: Path) -> Path:
    """Build one named figure into ``output_dir`` as ``<name>.svg``."""

    if name not in FIGURES:
        raise KeyError(f"unknown figure '{name}'; known: {sorted(FIGURES)}")
    svg = FIGURES[name]()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}.svg"
    path.write_text(svg, encoding="utf-8")
    return path


def build_all(output_dir: Path) -> list[Path]:
    """Build every registered figure; return the written paths sorted."""

    return [build_figure(name, output_dir) for name in sorted(FIGURES)]
