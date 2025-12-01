"""Agents package exports for convenience.

Expose commonly-used helpers so callers can `from agents import apply_patch_to_html`.
Also re-export small ADK wrapper creators for convenience in demos.
"""
from .patcher import apply_patch_to_html
from .adk_wrappers import create_fetch_html_tool, create_code_execution_tool

__all__ = [
    'apply_patch_to_html',
    'create_fetch_html_tool',
    'create_code_execution_tool',
]
