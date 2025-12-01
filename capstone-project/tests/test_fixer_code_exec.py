import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "capstone-project"))

from agents.fixer import suggest_fixes


def test_fixer_uses_code_exec_and_scanner(monkeypatch):
    """Ensure that a fixer can call tools['code_exec'] and tools['scanner'] when provided.

    We construct a fake scan_result with an alt_missing issue and provide a
    code_exec that records invocation. The builtin suggest_fixes applies
    verification via code_exec when patch contains alt or <h1>.
    """
    called = {}

    def fake_code_exec(code: str):
        called["code_exec"] = True
        return {"stdout": "ok\n", "stderr": "", "returncode": 0}

    def fake_scanner(html: str, url: str):
        called["scanner"] = True
        # Return no issues to simulate successful post-scan
        return {"issues": [], "summary": "0 issue(s) found"}

    scan_result = {
        "issues": [
            {
                "id": "alt_missing",
                "message": "Image missing alt",
                "selector": "img:nth-of-type(1)",
            }
        ],
        "summary": "1 issue(s) found",
    }

    html = '<html><body><img src="/img/x.png"></body></html>'

    suggestions = suggest_fixes(
        scan_result, html, tools={"code_exec": fake_code_exec, "scanner": fake_scanner}
    )

    # The built-in suggest_fixes should have attempted code_exec for alt_missing
    assert isinstance(suggestions, list)
    assert any("verification" in s for s in suggestions)
    assert called.get("code_exec", False) is True
    assert called.get("scanner", False) is True
