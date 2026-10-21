from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from silver_line.formalism import generate
    return generate(ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
