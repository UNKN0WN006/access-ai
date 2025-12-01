"""Fixer skeleton: produce simple suggested HTML snippets for top issues.
This module returns suggested attributes/snippets and supports a demo-only
apply-and-verify flow that applies small heuristic patches and re-runs the
scanner to show any reduction in detected issues.
"""

import re
from typing import Any, Dict, List

from agents.patcher import apply_patch_to_html


def suggest_fixes(
    scan_result: Dict, html: str, tools: Dict[str, Any] = None
) -> List[Dict]:
    """Return suggested fixes and optionally apply + verify using provided tools.

    If `tools` contains `code_exec` and/or `scanner`, they will be used to
    produce small execution and re-scan verification metadata for each fix.
    """
    suggestions: List[Dict] = []
    code_exec = None
    scanner = None
    if tools:
        code_exec = tools.get("code_exec")
        scanner = tools.get("scanner")

    for issue in scan_result.get("issues", [])[:10]:
        patch = ""
        if issue["id"] == "alt_missing":
            patch = f'add alt to {issue.get("selector", "img")}'
            suggestion = 'Add alt attribute: alt="Describe image"'
        elif issue["id"] == "heading_structure":
            patch = "<h1>Page title</h1>"
            suggestion = "Ensure the page has a single H1 at top"
        elif issue["id"] in ("label_missing", "label_missing_id"):
            patch = "insert label for control"
            suggestion = "Add associated <label> or aria-label to form control"
        else:
            patch = ""
            suggestion = "Manual review recommended"

        item: Dict[str, Any] = {
            "issue": issue,
            "suggestion": suggestion,
            "patch": patch,
        }

        # Lightweight code_exec verification (demo only)
        if code_exec and patch and ("alt" in patch or "<h1>" in patch):
            if "alt" in patch:
                verify_code = "print('ok' if 'alt=' in '''%s''' else 'fail')" % patch
            else:
                verify_code = "print('ok' if '<h1>' in '''%s''' else 'fail')" % patch
            try:
                ver_res = code_exec(verify_code)
                if isinstance(ver_res, dict):
                    item["verification"] = {
                        "stdout": ver_res.get("stdout", "").strip(),
                        "returncode": ver_res.get("returncode"),
                    }
                else:
                    item["verification"] = {"stdout": str(ver_res), "returncode": 0}
            except Exception:
                item["verification"] = {"stdout": "", "returncode": -1}

        # Apply patch to a copy and re-run scanner to show reduction in issues
        if scanner and patch:
            new_html = apply_patch_to_html(html, issue, patch)
            try:
                post_scan = scanner(new_html, "")
                item["post_scan"] = post_scan
                item["reduction"] = len(scan_result.get("issues", [])) - len(
                    post_scan.get("issues", [])
                )
            except Exception:
                item["post_scan"] = {"issues": [], "summary": "scanner error"}
                item["reduction"] = 0

        suggestions.append(item)

    return suggestions


# Backwards-compatible alias for code that imported the private name
_apply_patch_to_html = apply_patch_to_html

__all__ = [
    "suggest_fixes",
    "apply_patch_to_html",
]
