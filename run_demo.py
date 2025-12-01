#!/usr/bin/env python3
"""Simple, reliable runner for the AccessAI demo.

This runner avoids ADK/session-service paths and calls the local orchestrate
flow used by the notebook. It is intended for quick, one-line reproducible
runs from the repository root:

  python run_demo.py

It writes patched HTML outputs to `capstone-project/tmp/` (creating the
directory if needed).
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import List

import sys
from pathlib import Path as _Path

# Ensure `capstone-project` package directory is on the import path
_root = _Path(__file__).parent
_pkg_path = _root / "capstone-project"
sys.path.insert(0, str(_pkg_path))

from agents.manager import orchestrate
from agents.scanner import analyze_html
from agents.fixer import suggest_fixes
from agents.eval import apply_patches_and_rescan, score_page
from agents.adk_wrappers import create_fetch_html_tool, create_code_execution_tool


LOG = logging.getLogger("accessai.runner")


def run_samples(samples: List[Path]) -> None:
    fetch_tool = create_fetch_html_tool()
    code_exec = create_code_execution_tool()

    out_dir = Path(__file__).parent / "capstone-project" / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in samples:
        print("Processing:", p.name)
        result = orchestrate(
            str(p),
            {
                "fetch_html": fetch_tool,
                "scanner": analyze_html,
                "fixer": suggest_fixes,
                "code_exec": code_exec,
            },
        )

        print("  Scan summary:", result["scan"].get("summary"))
        print("  Suggestions:")
        for s in result.get("fixes", []):
            print("   -", s.get("suggestion"))

        try:
            original_html = fetch_tool(str(p))
            final_html, post_scan = apply_patches_and_rescan(
                original_html, result.get("fixes", []), analyze_html
            )
            scoring = score_page(result.get("scan", {}), post_scan)
            print(
                f"  Score: before={scoring['total_before']} after={scoring['total_after']} reduction={scoring['total_reduction']}"
            )
            out_path = out_dir / f"patched_{p.name}"
            out_path.write_text(final_html, encoding="utf-8")
            print("  Patched HTML written to", out_path)
        except Exception as e:
            LOG.exception("Failed to apply patches for %s: %s", p.name, e)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AccessAI demo (offline)")
    parser.add_argument(
        "--samples",
        "-s",
        nargs="*",
        help="Optional list of sample filenames (relative to capstone-project/data/sample_pages)",
    )
    args = parser.parse_args()

    data_dir = Path(__file__).parent / "capstone-project" / "data" / "sample_pages"
    if args.samples:
        samples = [data_dir / s for s in args.samples]
    else:
        samples = sorted(list(data_dir.glob("*.html")))

    run_samples(samples)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
