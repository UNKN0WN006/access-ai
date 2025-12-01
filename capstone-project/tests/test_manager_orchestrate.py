import builtins
import sys
import types
from pathlib import Path

import pytest

# Ensure the `capstone-project` package is importable during tests
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "capstone-project"))

from agents.manager import orchestrate


def test_orchestrate_uses_fallback_tools(monkeypatch, tmp_path):
    """When `fetch_html` and `code_exec` are omitted, orchestrate should call fallback creators."""
    created = {}

    # Spy replacements for fallback creators
    def fake_create_fetch_html_tool():
        def fetch(path_or_url):
            created["fetch_called"] = True
            # Return a small HTML page
            return '<html><body><h1>Test</h1><img src="/img/x.png"></body></html>'

        return fetch

    def fake_create_code_execution_tool():
        def exec_code(code: str):
            created["code_exec_called"] = True
            return {"stdout": "", "stderr": "", "returncode": 0}

        return exec_code

    # Monkeypatch the manager module's creators so orchestrate uses them
    import agents.manager as mgr

    monkeypatch.setattr(mgr, "create_fetch_html_tool", fake_create_fetch_html_tool)
    monkeypatch.setattr(
        mgr, "create_code_execution_tool", fake_create_code_execution_tool
    )

    # Provide a trivial scanner that detects the image as missing alt
    def scanner(html_text, url):
        return {
            "issues": [
                {"id": "alt_missing", "message": "Image missing alt", "selector": "img"}
            ],
            "summary": "1 issue(s) found",
        }

    # Provide a fixer that checks it receives fixer_tools with code_exec and scanner
    def fixer(scan_result, html_text, tools=None):
        assert tools is not None
        # ensure fallback code_exec and scanner are present
        assert "code_exec" in tools
        assert callable(tools["code_exec"])
        assert "fetch_html" in tools
        assert callable(tools["fetch_html"])
        return [{"suggestion": "add alt", "patch": "add alt to img"}]

    sample_path = str(Path("capstone-project/data/sample_pages/good.html"))
    res = orchestrate(sample_path, {"scanner": scanner, "fixer": fixer})

    assert res["scan"]["summary"].endswith("issue(s) found")
    assert created.get("fetch_called", False) is True


def test_orchestrate_passes_provided_tools(monkeypatch):
    """When callers provide fetch_html and code_exec, they should be used and passed to fixer."""
    used = {}

    def provided_fetch(p):
        used["provided_fetch"] = True
        return "<html><body><h1>Provided</h1></body></html>"

    def provided_code_exec(code: str):
        used["provided_code_exec"] = True
        return {"stdout": "ok", "stderr": "", "returncode": 0}

    def scanner(html_text, url):
        return {"issues": [], "summary": "0 issue(s) found"}

    def fixer(scan_result, html_text, tools=None):
        # The provided tools should be forwarded
        assert tools is not None
        assert tools.get("fetch_html") is provided_fetch
        assert tools.get("code_exec") is provided_code_exec
        return []

    res = orchestrate(
        "capstone-project/data/sample_pages/good.html",
        {
            "fetch_html": provided_fetch,
            "scanner": scanner,
            "fixer": fixer,
            "code_exec": provided_code_exec,
        },
    )

    assert used.get("provided_fetch", False)
    assert res["scan"]["summary"].startswith("0 issue")
