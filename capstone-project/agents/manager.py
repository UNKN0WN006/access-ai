"""Manager agent skeleton: orchestrates fetch -> scan -> fix.

This module ensures `fetch_html` and `code_exec` tools are available by
using the ADK fallbacks when callers do not provide them. The orchestration
function remains small and deterministic so the demo can run offline.
"""
from typing import Dict, Any

from agents.adk_wrappers import create_fetch_html_tool, create_code_execution_tool


def orchestrate(url: str, tools: Dict[str, Any]):
    """High-level orchestration function used by the notebook/demo.

    tools: {
        'fetch_html': callable (optional),
        'scanner': callable,
        'fixer': callable,
        'code_exec': callable (optional),
        ...optional additional tools...
    }

    If `fetch_html` or `code_exec` are not provided, ADK fallbacks from
    `agents.adk_wrappers` will be used so the pipeline remains runnable.
    """
    # Provide safe fallbacks for optional tools
    fetch = tools.get('fetch_html') if tools and tools.get('fetch_html') else create_fetch_html_tool()
    code_exec = tools.get('code_exec') if tools and tools.get('code_exec') else create_code_execution_tool()

    html = fetch(url)
    scan_result = tools['scanner'](html, url)
    fixer = tools['fixer']

    # Ensure tools passed to the fixer include useful helpers
    fixer_tools = dict(tools or {})
    fixer_tools.setdefault('fetch_html', fetch)
    fixer_tools.setdefault('code_exec', code_exec)
    fixer_tools.setdefault('scanner', tools.get('scanner'))

    # Call fixer with tools dict when supported, else fallback to older signature
    try:
        fixes = fixer(scan_result, html, fixer_tools)
    except TypeError:
        fixes = fixer(scan_result, html)

    return {
        'url': url,
        'scan': scan_result,
        'fixes': fixes,
    }
