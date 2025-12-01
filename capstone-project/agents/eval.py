"""Evaluation helpers: scoring and apply+rescan utilities.

Provides simple, deterministic scoring used by the demo. Keep functions
small and easy to reason about.
"""
from typing import Dict, List, Tuple, Any

from agents.patcher import apply_patch_to_html


def _count_by_issue(scan: Dict) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for issue in scan.get("issues", []):
        key = issue.get("id", "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def score_page(scan_before: Dict, scan_after: Dict) -> Dict[str, Any]:
    """Compute simple per-category counts and reductions.

    Returns a dict with `before_counts`, `after_counts`, `reduction` per
    category and `total_before`, `total_after`, `total_reduction`.
    """
    before = _count_by_issue(scan_before or {})
    after = _count_by_issue(scan_after or {})

    reduction: Dict[str, int] = {}
    keys = set(before.keys()) | set(after.keys())
    total_before = 0
    total_after = 0
    for k in keys:
        b = before.get(k, 0)
        a = after.get(k, 0)
        reduction[k] = b - a
        total_before += b
        total_after += a

    return {
        "before_counts": before,
        "after_counts": after,
        "reduction": reduction,
        "total_before": total_before,
        "total_after": total_after,
        "total_reduction": total_before - total_after,
    }


def apply_patches_and_rescan(html: str, suggestions: List[Dict], scanner: Any) -> Tuple[str, Dict]:
    """Apply a sequence of suggested patches to `html` and re-run `scanner`.

    Suggestions are expected to be dicts that include an `issue` key and a
    `patch` (human-readable or snippet). We use `apply_patch_to_html` to
    make conservative edits. The scanner callable must accept `(html, url)`
    or `(html,)` and return a scan dict.
    """
    cur = html
    for s in suggestions:
        issue = s.get("issue") or {}
        patch = s.get("patch") or ""
        try:
            cur = apply_patch_to_html(cur, issue, patch)
        except Exception:
            # keep going on errors; demo must be robust
            continue

    # Rerun scanner
    try:
        # support both scanner(html, url) and scanner(html)
        scan_after = scanner(cur, "") if getattr(scanner, "__code__", None) and scanner.__code__.co_argcount >= 2 else scanner(cur)
    except Exception:
        scan_after = {"issues": [], "summary": "scanner error"}

    return cur, scan_after


__all__ = ["score_page", "apply_patches_and_rescan"]
