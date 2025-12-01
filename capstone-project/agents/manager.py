"""Manager: orchestrate fetch -> scan -> fix with safe fallbacks."""

from typing import Any, Dict

from agents.adk_wrappers import (create_code_execution_tool,
                                 create_fetch_html_tool)


def orchestrate(url: str, tools: Dict[str, Any]):
    """Orchestrate a scan and return structured results.

    `tools` should include `scanner` and `fixer`. Optional helpers
    `fetch_html` and `code_exec` will be provided as fallbacks.
    """
    # Provide safe fallbacks for optional tools
    fetch = (
        tools.get("fetch_html")
        if tools and tools.get("fetch_html")
        else create_fetch_html_tool()
    )
    code_exec = (
        tools.get("code_exec")
        if tools and tools.get("code_exec")
        else create_code_execution_tool()
    )

    html = fetch(url)
    scan_result = tools["scanner"](html, url)
    fixer = tools["fixer"]

    # Ensure tools passed to the fixer include useful helpers
    fixer_tools = dict(tools or {})
    fixer_tools.setdefault("fetch_html", fetch)
    fixer_tools.setdefault("code_exec", code_exec)
    fixer_tools.setdefault("scanner", tools.get("scanner"))

    # Call fixer with tools dict when supported, else fallback to older signature
    try:
        fixes = fixer(scan_result, html, fixer_tools)
    except TypeError:
        fixes = fixer(scan_result, html)

    return {
        "url": url,
        "scan": scan_result,
        "fixes": fixes,
    }
