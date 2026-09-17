import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import report  # noqa: E402

EXAMPLES = report.REPO_DIR / "examples"
REPORTABLE = sorted(p for p in EXAMPLES.glob("*.json") if p.name != "example.json")


@pytest.mark.parametrize("path", REPORTABLE, ids=lambda p: p.stem)
def test_example_renders(path):
    html = report.render(report.summarize(*report.load(path)), path.name)
    assert "Energy Performance Report" in html


def test_courthouse_totals():
    totals = report.summarize(*report.load(EXAMPLES / "courthouse_proposed.json"))["totals"]
    assert round(totals["consumption"]) == 868_222
    assert round(totals["production"]) == 639_126
    assert round(totals["unregulated"]) == 271_991
    assert round(totals["net"]) == 229_095


def test_monthly_file_matches_hourly_file():
    hourly = report.summarize(*report.load(EXAMPLES / "courthouse_proposed.json"))
    monthly = report.summarize(*report.load(EXAMPLES / "courthouse_proposed_monthly.json"))
    assert monthly["period"]["resolution"] == "12 monthly intervals"
    for key in ("monthly_end_use", "monthly_source"):
        assert monthly[key].round(0).equals(hourly[key].round(0))


def test_annual_file_skips_monthly_section(tmp_path):
    doc = json.loads((EXAMPLES / "courthouse_proposed_monthly.json").read_text(encoding="utf-8"))
    doc["time_intervals"] = [{"id": "Annual", "starting_time": "2021-01-01T00:00Z", "regular_interval": 31536000.0}]

    def to_annual(end_uses):
        for end_use in end_uses:
            if "consumption" in end_use:
                end_use["consumption"]["values"] = [sum(end_use["consumption"]["values"])]
                end_use["consumption"]["value_time_intervals"] = "Annual"
            to_annual(end_use.get("subcategories", []))

    for source in doc["energy_sources"]:
        to_annual(source["end_uses"])
    path = tmp_path / "annual.json"
    path.write_text(json.dumps(doc), encoding="utf-8")

    summary = report.summarize(*report.load(path))
    assert summary["monthly_end_use"] is None
    assert round(summary["totals"]["consumption"]) == 868_222
    assert "Monthly Energy" not in report.render(summary, path.name)


def test_short_period_is_rejected():
    with pytest.raises(report.UnsupportedFile):
        report.load(EXAMPLES / "example.json")


def test_zero_consumption_is_flagged():
    checks = report.summarize(*report.load(EXAMPLES / "courthouse_proposed.json"))["checks"]
    assert "Electricity › Space Heating: reported as zero for the whole period." in [c["message"] for c in checks]


def test_recommended_colors_cover_canonical_names():
    sources, end_uses = report.canonical_order()
    assert set(report.END_USE_COLORS) == set(end_uses)
    assert set(report.SOURCE_COLORS) == set(sources)


def test_example_reports_are_published():
    """Each example's report is excluded from the report/output/ ignore rule, so it gets committed."""
    gitignore = (report.REPO_DIR / ".gitignore").read_text(encoding="utf-8").splitlines()
    for path in REPORTABLE:
        assert f"!report/output/{path.stem}.html" in gitignore, f"add !report/output/{path.stem}.html to .gitignore"
