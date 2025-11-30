"""Agents package exports for convenience.

Expose commonly-used helpers so callers can `from agents import apply_patch_to_html`.
"""
from .patcher import apply_patch_to_html

__all__ = [
    'apply_patch_to_html',
]
