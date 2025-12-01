import os
import sys
from pathlib import Path

# Ensure the capstone-project directory is on sys.path (match existing tests)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents import fixer as fixer_mod
from agents import scanner as scanner_mod
from agents.patcher import apply_patch_to_html

DATA_DIR = Path(__file__).parent.parent / "data" / "sample_pages"


def _load(name: str) -> str:
    return (DATA_DIR / name).read_text(encoding="utf-8")


def test_medium_page_has_reduction_from_fix():
    html = _load("medium.html")
    before = scanner_mod.analyze_html(html, "")
    assert len(before.get("issues", [])) > 0

    suggestions = fixer_mod.suggest_fixes(
        before, html, tools={"scanner": scanner_mod.analyze_html}
    )
    assert suggestions, "Expected at least one suggestion"

    # At least one suggestion should show a positive reduction in issues
    assert any(
        s.get("reduction", 0) > 0 for s in suggestions
    ), "No suggestion produced a positive reduction"

    # Extra safety: ensure that for at least one suggestion the post-scan no longer
    # contains the original issue id (use post_scan if provided)
    ok = False
    for s in suggestions:
        orig_id = s.get("issue", {}).get("id")
        post = s.get("post_scan")
        if not post:
            # apply patch and re-scan using public patcher API
            new_html = apply_patch_to_html(html, s.get("issue", {}), s.get("patch", ""))
            post = scanner_mod.analyze_html(new_html, "")
        if not any(i.get("id") == orig_id for i in post.get("issues", [])):
            ok = True
            break
    assert (
        ok
    ), "No suggestion resulted in a post-scan that removed the original issue id"


def test_bad_page_has_reduction_from_fix():
    html = _load("bad.html")
    before = scanner_mod.analyze_html(html, "")
    assert len(before.get("issues", [])) > 0

    suggestions = fixer_mod.suggest_fixes(
        before, html, tools={"scanner": scanner_mod.analyze_html}
    )
    assert suggestions, "Expected at least one suggestion"

    assert any(
        s.get("reduction", 0) > 0 for s in suggestions
    ), "No suggestion produced a positive reduction"

    ok = False
    for s in suggestions:
        orig_id = s.get("issue", {}).get("id")
        post = s.get("post_scan")
        if not post:
            new_html = apply_patch_to_html(html, s.get("issue", {}), s.get("patch", ""))
            post = scanner_mod.analyze_html(new_html, "")
        if not any(i.get("id") == orig_id for i in post.get("issues", [])):
            ok = True
            break
    assert (
        ok
    ), "No suggestion resulted in a post-scan that removed the original issue id"
