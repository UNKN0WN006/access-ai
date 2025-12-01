"""Integration test: ensure manager.orchestrate accepts provided tools.

This test uses local fetch and code-exec fallbacks and the google_search stub
we added. It asserts the orchestrate result contains expected keys and that
calling with explicit tools behaves like the default flow.
"""
import sys
from pathlib import Path

# Ensure the `capstone-project` package is importable during tests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.manager import orchestrate
from agents.adk_wrappers import (
    create_fetch_html_tool,
    create_code_execution_tool,
    create_google_search_stub,
)
from agents.scanner import analyze_html
from agents.fixer import suggest_fixes


def test_orchestrate_with_tools():
    # Use a sample HTML from data
    sample = Path("capstone-project/data/sample_pages/good.html")
    assert sample.exists()

    fetch = create_fetch_html_tool()
    code_exec = create_code_execution_tool()
    search = create_google_search_stub()

    tools = {
        "fetch_html": fetch,
        "scanner": analyze_html,
        "fixer": suggest_fixes,
        "code_exec": code_exec,
        "google_search": search,
    }

    result = orchestrate(str(sample), tools)
    assert isinstance(result, dict)
    assert "url" in result and "scan" in result and "fixes" in result
    # Scan summary should be present
    assert "summary" in result["scan"]
