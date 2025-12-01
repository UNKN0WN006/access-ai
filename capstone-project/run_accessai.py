"""Example runner for AccessAI.

This script demonstrates two running modes:
 - Offline demo mode: uses local scanner + fixer + orchestrate function.
 - ADK mode: if `google-adk` is installed and configured, it will create LLM agents
   and show where to plug them in. ADK usage requires setting up API keys and
   installing `google-adk` and `google-genai`.

Run:
    python run_accessai.py --mode demo
    python run_accessai.py --mode adk   # only if ADK is installed and configured
"""

import argparse
import logging
from pathlib import Path

# New ADK-specific helpers (if ADK is present these return ADK objects)
from agents.adk_wrappers import (
    create_adk_fixer_agent_from_instruction,
    create_adk_scanner_tool,
    create_code_execution_tool,
    create_fetch_html_tool,
    create_fixer_agent,
    create_function_tool_py,
    create_manager_agent,
    create_memory_service,
    create_session_service,
    run_adk_flow,
    run_with_runner,
)
from agents.fixer import suggest_fixes
from agents.manager import orchestrate
from agents.scanner import analyze_html
from agents.eval import score_page, apply_patches_and_rescan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("accessai")

DATA_DIR = Path(__file__).parent / "data" / "sample_pages"


def demo_mode():
    logger.info("Running in demo (offline) mode using local functions")
    # Create lightweight session & memory services for the demo
    session_service = create_session_service()
    memory_service = create_memory_service()

    # Use the fetch_html tool so manager orchestration can call it uniformly.
    fetch_tool = create_fetch_html_tool()
    # Add a small code execution tool (demo only)
    code_exec = create_code_execution_tool()

    for sample in ["good.html", "medium.html", "bad.html"]:
        path = DATA_DIR / sample
        # orchestrate expects tools dict with 'fetch_html' callable
        result = orchestrate(
            str(path),
            {
                "fetch_html": fetch_tool,
                "scanner": analyze_html,
                "fixer": suggest_fixes,
                "code_exec": code_exec,
            },
        )
        # Store session events and memory summary
        session_id = f"audit:{sample}"
        session_service.create_session(session_id)
        session_service.append_event(
            session_id, {"stage": "scan", "summary": result["scan"]["summary"]}
        )
        memory_key = f"memory:{sample}"
        memory_service.write(
            memory_key, {"url": str(path), "summary": result["scan"]["summary"]}
        )
        logger.info("---")
        logger.info("URL: %s", result["url"])
        logger.info("Summary: %s", result["scan"]["summary"])
        for issue in result["scan"]["issues"]:
            logger.debug("- %s", issue["message"])
        logger.info("Suggestions:")
        for s in result["fixes"]:
            logger.info(" * %s", s.get("suggestion"))

        # Apply suggested patches sequentially, re-run scanner, and score.
        try:
            original_html = fetch_tool(str(path))
            final_html, post_scan = apply_patches_and_rescan(
                original_html, result.get("fixes", []), analyze_html
            )
            scoring = score_page(result.get("scan", {}), post_scan)
            logger.info(
                "Score: before=%d after=%d reduction=%d",
                scoring["total_before"],
                scoring["total_after"],
                scoring["total_reduction"],
            )
            # write patched HTML for review
            out_dir = Path(__file__).parent / "tmp"
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / f"patched_{sample}"
            out_path.write_text(final_html, encoding="utf-8")
            logger.info("Patched HTML written to %s", out_path)
        except Exception:
            logger.exception("Scoring or patch write failed")

    # Show stored memory content
    logger.info("\nStored memory items:")
    all_mem = memory_service.read_all()
    for k, v in all_mem.items():
        logger.info("- %s -> %s", k, v)


def adk_mode():
    logger.info("Attempting ADK mode (requires google-adk and credentials)")
    # Create ADK-compatible tools (or fallbacks)
    # Prefer ADK-wrapped fetch tool when available
    fetch_tool = create_fetch_html_tool()
    # Convert scanner into an ADK FunctionTool when possible
    scanner_tool = create_adk_scanner_tool(analyze_html)
    # Create a fixer LLM agent (ADK-backed if available, fallback otherwise)
    fixer_agent = create_adk_fixer_agent_from_instruction()
    manager_agent = create_manager_agent()
    # Create session & memory services (ADK or fallback)
    session_service = create_session_service()
    memory_service = create_memory_service()

    # Demonstrate ADK flow: run via InMemoryRunner when ADK installed, else fallback
    sample = DATA_DIR / "bad.html"
    adk_result = run_adk_flow(manager_agent, scanner_tool, fixer_agent, str(sample))

    if adk_result.get("manager_output") is not None:
        logger.info("Manager output (ADK runner):")
        logger.info("%s", adk_result["manager_output"])
    else:
        scan = adk_result.get("scan")
        fixes = adk_result.get("fixes")
        logger.info("\nScan summary: %s", scan.get("summary"))
        logger.info("Fix suggestions:")
        for s in fixes:
            # s may be dict or text depending on fixer implementation
            if isinstance(s, dict):
                logger.info("- %s", s.get("suggestion"))
            else:
                logger.info("- %s", s)

    # Persist audit summary in memory
    memory_key = f"adk:bad.html"
    try:
        memory_service.write(
            memory_key, {"summary": scan["summary"], "url": str(sample)}
        )
        logger.info("\nMemory written: %s", memory_key)
    except Exception:
        logger.exception("Failed to write memory")

    # Show session events (if any)
    try:
        session_service.create_session("adk-demo")
        session_service.append_event(
            "adk-demo", {"action": "scanned bad.html", "summary": scan["summary"]}
        )
        logger.info(
            "\nSession events for adk-demo: %s", session_service.get_events("adk-demo")
        )
    except Exception:
        logger.exception("Session service calls failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "adk"], default="demo")
    args = parser.parse_args()

    if args.mode == "demo":
        demo_mode()
    else:
        adk_mode()


if __name__ == "__main__":
    main()
