from dataclasses import replace
import json
from pathlib import Path

import pytest

from silver_line import SuccessionItem, read_succession, read_succession_with_findings
from silver_line.registry import SILVER_KEEPSAKES
from silver_line.serialization import canonical_verdict, verdict_digest


def test_sl04_changed_custodian_changes_report_identity():
    a = SuccessionItem("notebooks", "first", frozenset({"record"}))
    b = replace(a, custodian="second")
    assert verdict_digest(read_succession(a)) != verdict_digest(read_succession(b))


def test_sl04_changed_description_changes_report_identity():
    a = SuccessionItem("notebooks", "first", frozenset({"record"}))
    assert verdict_digest(read_succession(a)) != verdict_digest(read_succession(replace(a, description="letters")))


@pytest.mark.parametrize("api", [read_succession, read_succession_with_findings])
@pytest.mark.parametrize("registry", [SILVER_KEEPSAKES, ()])
def test_sl05_review_date_survives_every_branch(api, registry):
    result = api([], registry, evaluated_as_of="2026-10-20", subject_id="subject")
    verdict = result[0] if isinstance(result, tuple) else result
    assert json.loads(canonical_verdict(verdict))["evaluated_as_of"] == "2026-10-20"


def test_sl06_permutations_have_identical_reports():
    items = [SuccessionItem("a", "one", frozenset({"record"})),
             SuccessionItem("b", "two", frozenset({"artifact", "unknown"}))]
    a = read_succession(items)
    b = read_succession(list(reversed(items)), tuple(reversed(SILVER_KEEPSAKES)))
    assert canonical_verdict(a) == canonical_verdict(b)


def test_sl07_shipped_reports_are_retrievable_and_match_status():
    root = Path(__file__).resolve().parents[1]
    envelopes = [json.loads(p.read_text()) for p in sorted((root / "data/envelopes").glob("*.json"))]
    assert len({e["report_ref"] for e in envelopes}) == len(envelopes)
    for envelope in envelopes:
        report = json.loads((root / "data/reports" / (envelope["report_ref"] + ".json")).read_text())
        assert report["status"] == envelope["native_status"]
