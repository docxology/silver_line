"""Build every registered Silver Line figure into output/figures/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for entry in (str(ROOT), str(ROOT / "src")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from silver_line.figures.build import (  # noqa: E402
    build_all,
    figure_registry,
    rasterize_cover,
)


def main() -> int:
    output_dir = ROOT / "output" / "figures"
    written = build_all(output_dir) + [rasterize_cover(output_dir)]
    registry = figure_registry()
    (output_dir / "figure_registry.json").write_text(
        __import__("json").dumps(registry, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for path in sorted(written):
        print(f"built {path.relative_to(ROOT)}")
    print(
        f"built output/figures/figure_registry.json ({len(registry['figures'])} figures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
