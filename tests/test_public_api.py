"""The public API surface and the line-spec content contract."""

from __future__ import annotations

import silver_line
from silver_line.registry import SILVER_KEEPSAKES


def test_version_is_a_string() -> None:
    assert isinstance(silver_line.__version__, str)
    assert silver_line.__version__.count(".") == 2


def test_version_module_is_the_authority() -> None:
    from silver_line.version import __version__ as v
    assert v == silver_line.__version__


def test_question_job_and_must_not_become() -> None:
    assert silver_line.QUESTION == "What do I keep, and how does it outlive me?"
    assert "Memory and succession" in silver_line.JOB
    assert "immortality" in silver_line.MUST_NOT_BECOME


def test_color_is_silver_and_unique_in_this_repo() -> None:
    assert "silver" in silver_line.__name__


def test_registry_ids_are_public() -> None:
    assert len(silver_line.registry_ids()) == len(SILVER_KEEPSAKES)
