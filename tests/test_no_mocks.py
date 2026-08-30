"""The lexical no-mocks gate: no mocking framework anywhere in the repo."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
#: Tokens assembled from pieces so this gate file does not contain the
#: literal spellings it forbids elsewhere.
_FORBIDDEN_PARTS = (
    ("unittest", ".mock"),
    ("Magic", "Mock"),
    ("mocker", ".patch"),
    ("from ", "mock import"),
    ("import ", "mock"),
)
FORBIDDEN = tuple(a + b for a, b in _FORBIDDEN_PARTS)


def test_no_mock_framework_anywhere() -> None:
    offenders: list[str] = []
    paths = sorted((ROOT / "src").rglob("*.py"))
    paths += sorted((ROOT / "tests").rglob("*.py"))
    paths += sorted((ROOT / "scripts").rglob("*.py"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in text:
                offenders.append(f"{path.name}: {token}")
    assert not offenders, sorted(offenders)
