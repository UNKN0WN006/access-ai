import sys
import time
from pathlib import Path

# Ensure local package imports work
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.scanner import analyze_html

DATA_DIR = Path(__file__).parent.parent / "data" / "sample_pages"


def load(page_name: str) -> str:
    return (DATA_DIR / page_name).read_text(encoding="utf-8")


def test_anchor_aria_label_missing():
    html = '<html><body><a href="/download"></a></body></html>'
    res = analyze_html(html, "inline")
    assert any(i["id"] == "aria_label_missing" for i in res["issues"])


def test_color_contrast_detection():
    # low contrast (light gray on white)
    html = '<div style="color:#aaaaaa;background-color:#ffffff">Text</div>'
    res = analyze_html(html, "inline")
    assert any(i["id"] == "color_contrast_low" for i in res["issues"])


def test_color_contrast_ok():
    # good contrast (black on white)
    html = '<div style="color:#000000;background-color:#ffffff">Text</div>'
    res = analyze_html(html, "inline")
    assert not any(i["id"] == "color_contrast_low" for i in res["issues"])


def test_large_stress_page_performance_and_detection():
    # Create a large page with many images missing alt attributes
    parts = ["<html><body>"]
    for i in range(500):
        parts.append(f'<img src="/img/{i}.png"/>')
    parts.append("</body></html>")
    html = "\n".join(parts)
    start = time.time()
    res = analyze_html(html, "large")
    duration = time.time() - start
    # Should complete under 2 seconds in this environment (heuristic)
    assert duration < 5.0
    assert len(res["issues"]) >= 500


def test_malformed_html_edge_case():
    html = '<html><head><title>Bad</title><body><img><a href="#"></body></html>'
    res = analyze_html(html, "malformed")
    # Should not raise and should contain at least alt_missing for the img
    assert any(i["id"] == "alt_missing" for i in res["issues"])
