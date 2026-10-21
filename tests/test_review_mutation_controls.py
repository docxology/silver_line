from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("file,old,new,test", [
    ("evaluator.py", "lapse eligible but not yet declared; unresolved, not a retention defect", "gap", "test_review_boundaries.py::test_sl03_silence_is_not_a_declared_release"),
    ("evaluator.py", "tags=tags & KEEPSAKE_TAG_VOCABULARY", "tags=tags", "test_review_boundaries.py::test_sl02_unknown_tags_are_actually_filtered"),
    ("evaluator.py", 'item.item_id, fields + missing', '"", fields + missing', "test_review_acceptance.py::test_duplicate_ids_reject_entire_scan_and_counts_qualify_scope"),
    ("artifacts.py", '"native_status": verdict.status.value', '"native_status": "MUTATED"', "test_review_identity.py::test_sl07_shipped_reports_are_retrievable_and_match_status"),
])
def test_semantic_checks_reject_source_mutations(tmp_path, file, old, new, test):
    for directory in ("src", "tests", "data"):
        shutil.copytree(ROOT / directory, tmp_path / directory, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "pyproject.toml", tmp_path / "pyproject.toml")
    path = tmp_path / "src/silver_line" / file
    text = path.read_text()
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    if file == "artifacts.py":
        generated = subprocess.run([sys.executable, "-m", "silver_line.artifacts"], cwd=tmp_path,
                                   env={"PATH": str(Path(sys.executable).parent), "PYTHONPATH": str(tmp_path / "src")},
                                   capture_output=True, text=True)
        assert generated.returncode == 0, generated.stderr
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/" + test], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "FAILED" in result.stdout
