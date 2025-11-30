"""Manager agent skeleton: orchestrates fetch -> scan -> fix."""
from typing import Dict, Any


def orchestrate(url: str, tools: Dict[str, Any]):
    """High-level orchestration function used by the notebook/demo.

    tools: {
        'fetch_html': callable,
        'scanner': callable,
        'fixer': callable,
        ...optional additional tools...
    }
    """
    html = tools['fetch_html'](url)
    scan_result = tools['scanner'](html, url)
    fixer = tools['fixer']
    # Call fixer with tools dict when supported, else fallback to older signature
    try:
        fixes = fixer(scan_result, html, tools)
    except TypeError:
        fixes = fixer(scan_result, html)

    return {
        'url': url,
        'scan': scan_result,
        'fixes': fixes,
    }
