"""The figure registry and deterministic SVG figure builders.

Every builder derives its content from the live keepsake registry, sorts
every emitted sequence, and writes deterministic SVG. A figure is a reading
aid, not evidence; captions in the manuscript say what each one does and
does not show.
"""

import os
import subprocess
from pathlib import Path

from ..enums import KeepKind
from ..registry import KEEPSAKE_TAG_VOCABULARY, SILVER_KEEPSAKES
from ..records import Keepsake



#: The cover palette. silver_line keeps no palette module of its own, so the
#: cover borrows the family's house ground (cream paper, dark ink, muted
#: rule) and carries one muted silver as the work's stroke colour.
COVER_PAPER = "#f5e6d3"
COVER_INK = "#211c1b"
COVER_MUTED = "#5a504a"
COVER_RULE = "#b7a894"
COVER_SILVER = "#8f939b"

#: The cover canvas matches the sibling covers' title-page proportions.
COVER_WIDTH = 1800
COVER_HEIGHT = 1100

#: The only text the cover carries, per the family's cover convention.
COVER_TITLE = "SILVER LINE"
COVER_TAGLINE = "WHAT IS PRESERVED, WHAT IS ENTRUSTED, WHAT MAY LAPSE"

#: The rasterizer used to produce the cover PNG from its deterministic SVG.
RSVG_CONVERT = "rsvg-convert"

#: The figure name the cover plate is registered and published under.
COVER_FIGURE = "silver_line_cover"


def _cover_text(
    x: float,
    y: float,
    value: str,
    size: int,
    fill: str,
    weight: str,
    anchor: str,
) -> str:
    """One cover text run, rendered small-caps by capitalising the source."""
    return (
        f'<text x="{x:g}" y="{y:g}" font-family="Arial, sans-serif" '
        f'font-size="{size}px" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}" letter-spacing="3">{value}</text>'
    )


def build_line_cover_figure() -> str:
    """Render the cover plate: memory and succession in three silver strokes.

    Three horizontal strokes across the cream field carry the succession
    picture the tagline names, read top to bottom. The preserved stroke is
    solid and heavy end to end. The entrusted stroke hands itself down: it
    descends at a node and continues on the lower level. The lapsing stroke
    dissolves — solid, then dashed and fading, then absent before the row's
    end. No row is labelled; the tagline is the only legend, and the cover
    carries no date and no version.
    """
    # Stroke caps land exactly on the text margins: round caps add half a
    # stroke width (15) to each end, so the geometry is inset by 15.
    left, right = 135.0, 1665.0
    body = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{COVER_WIDTH}" height="{COVER_HEIGHT}" '
            f'viewBox="0 0 {COVER_WIDTH} {COVER_HEIGHT}" role="img" '
            f'aria-labelledby="cover-title cover-desc">'
        ),
        (
            '<title id="cover-title">silver_line cover</title>'
            '<desc id="cover-desc">Three silver strokes across a cream '
            'field: one preserved whole, one entrusting itself downward '
            'at a node, one dissolving into dashes before its end.</desc>'
        ),
        f'<rect width="{COVER_WIDTH}" height="{COVER_HEIGHT}" '
        f'fill="{COVER_PAPER}"/>',
        (
            f'<rect x="60" y="60" width="{COVER_WIDTH - 120}" '
            f'height="{COVER_HEIGHT - 120}" fill="none" '
            f'stroke="{COVER_RULE}" stroke-width="2.5"/>'
        ),
        _cover_text(
            120, 168, COVER_TITLE, 44, COVER_INK, "700", "start"
        ),
    ]

    # Preserved: one continuous, heavy stroke, end to end.
    body.append(
        f'<line x1="{left:g}" y1="460" x2="{right:g}" y2="460" '
        f'stroke="{COVER_SILVER}" stroke-width="30" '
        f'stroke-linecap="round"/>'
    )

    # Entrusted: the stroke hands itself down at a node and continues below.
    body.append(
        f'<path d="M {left:g} 660 H 800 L 870 715 H {right:g}" '
        f'fill="none" stroke="{COVER_SILVER}" stroke-width="30" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )
    body.append(
        f'<circle cx="870" cy="715" r="20" fill="{COVER_PAPER}" '
        f'stroke="{COVER_SILVER}" stroke-width="12"/>'
    )

    # May lapse: solid, then dashed and fading, then absent.
    body.append(
        f'<line x1="{left:g}" y1="860" x2="650" y2="860" '
        f'stroke="{COVER_SILVER}" stroke-width="30" '
        f'stroke-linecap="round"/>'
    )
    body.append(
        f'<line x1="710" y1="860" x2="1050" y2="860" '
        f'stroke="{COVER_SILVER}" stroke-width="30" stroke-linecap="round" '
        f'stroke-dasharray="44 36" opacity="0.7"/>'
    )
    body.append(
        f'<line x1="1110" y1="860" x2="1280" y2="860" '
        f'stroke="{COVER_SILVER}" stroke-width="30" stroke-linecap="round" '
        f'stroke-dasharray="20 42" opacity="0.45"/>'
    )

    body.append(
        _cover_text(
            COVER_WIDTH - 120,
            COVER_HEIGHT - 110,
            COVER_TAGLINE,
            30,
            COVER_MUTED,
            "400",
            "end",
        )
    )
    body.append("</svg>")
    return "".join(body)


def rasterize_cover(output_dir: Path) -> Path:
    """Rasterize the built cover SVG to PNG; return the PNG path."""

    svg_path = output_dir / f"{COVER_FIGURE}.svg"
    png_path = output_dir / f"{COVER_FIGURE}.png"
    executable = os.environ.get("SILVER_LINE_RSVG_CONVERT", RSVG_CONVERT)
    try:
        subprocess.run(
            [executable, "-o", str(png_path), str(svg_path)], check=True
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            f"{executable!r} could not render {COVER_FIGURE}; install "
            "librsvg so rsvg-convert is on PATH."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            f"{executable!r} failed while rendering {COVER_FIGURE}; "
            "install or repair librsvg and rerun the figure build."
        ) from error
    return png_path

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
    "silver_line_cover": build_line_cover_figure,
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
