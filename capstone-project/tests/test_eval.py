"""Test for evaluation helpers."""
from pathlib import Path
import sys

# ensure capstone-project is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.scanner import analyze_html
from agents.adk_wrappers import create_fetch_html_tool
from agents.fixer import suggest_fixes
from agents.eval import apply_patches_and_rescan, score_page


def test_apply_patches_and_score():
    repo_root = Path(__file__).resolve().parents[1]
    sample = repo_root / "data" / "sample_pages" / "bad.html"
    assert sample.exists()

    fetch = create_fetch_html_tool()
    html = fetch(str(sample))
    before = analyze_html(html, str(sample))

    fixes = suggest_fixes(before, html, {"scanner": analyze_html})
    final_html, after = apply_patches_and_rescan(html, fixes, analyze_html)

    scoring = score_page(before, after)
    assert scoring["total_after"] <= scoring["total_before"]
