import sys
from pathlib import Path

import pytest

# Ensure the repository's capstone-project package dir is on sys.path for tests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.scanner import analyze_html

DATA_DIR = Path(__file__).parent.parent / "data" / "sample_pages"


def load(page_name: str) -> str:
    return (DATA_DIR / page_name).read_text(encoding="utf-8")


def test_good_page_has_no_issues():
    html = load("good.html")
    result = analyze_html(html, "good.html")
    assert "issues" in result
    assert isinstance(result["issues"], list)
    assert len(result["issues"]) == 0


def test_medium_page_detects_expected_issues():
    html = load("medium.html")
    result = analyze_html(html, "medium.html")
    issues = result["issues"]
    # Expect at least 3 issues: missing alt, missing H1, missing label for input id
    assert any(i["id"] == "alt_missing" for i in issues)
    assert any(i["id"] == "heading_structure" for i in issues)
    assert any(i["id"] in ("label_missing", "label_missing_id") for i in issues)


def test_bad_page_detects_critical_issues():
    html = load("bad.html")
    result = analyze_html(html, "bad.html")
    issues = result["issues"]
    # Bad page should have image without alt and missing form control id
    assert any(i["id"] == "alt_missing" for i in issues)
    assert any(i["id"] in ("label_missing_id", "label_missing") for i in issues)
    assert any(i["id"] == "heading_structure" for i in issues)
