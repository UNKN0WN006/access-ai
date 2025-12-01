"""Agents package exports for convenience.

Expose commonly-used helpers so callers can `from agents import apply_patch_to_html`.
Also re-export small ADK wrapper creators for convenience in demos.
"""

from .adk_wrappers import create_code_execution_tool, create_fetch_html_tool, create_google_search_stub
from .patcher import apply_patch_to_html

__all__ = [
    "apply_patch_to_html",
    "create_fetch_html_tool",
    "create_code_execution_tool",
    "create_google_search_stub",
]
