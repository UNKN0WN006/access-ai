"""ADK wrappers and fallbacks for AccessAI.

Provides optional ADK integrations and safe local fallbacks so the demo
runs without external credentials.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict

import requests

logger = logging.getLogger(__name__)

try:
    # ADK imports - optional
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.adk.tools.function_tool import FunctionTool
    from google.genai import types

    ADK_AVAILABLE = True
    logger.info("ADK libraries available")
except Exception as e:
    ADK_AVAILABLE = False
    logger.info("ADK not available, using fallback. (%s)", e)


def create_function_tool_py(func: Callable, name: str, description: str):
    """Return an ADK FunctionTool when available, otherwise the raw function."""
    if ADK_AVAILABLE:
        # Create a thin FunctionTool wrapper for ADK
        try:
            ft = FunctionTool(name=name, func=func, description=description)
            return ft
        except Exception:
            logger.exception(
                "Failed to create ADK FunctionTool, returning raw function"
            )
            return func
    else:
        return func


def _local_fetch(path_or_url: str) -> str:
    """Fetch HTML from disk or HTTP(S)."""
    try:
        if str(path_or_url).startswith("http://") or str(path_or_url).startswith(
            "https://"
        ):
            resp = requests.get(path_or_url, timeout=5)
            resp.raise_for_status()
            return resp.text
        else:
            return Path(path_or_url).read_text(encoding="utf-8")
    except Exception:
        logger.exception("Failed to fetch path_or_url: %s", path_or_url)
        return ""


def create_fetch_html_tool(
    name: str = "fetch_html", description: str = "Fetch HTML from path or URL"
):
    """Return an ADK FunctionTool for fetching HTML or a callable fallback."""
    if ADK_AVAILABLE:
        try:
            ft = FunctionTool(name=name, func=_local_fetch, description=description)
            return ft
        except Exception:
            logger.exception(
                "Failed to create ADK FunctionTool for fetch_html; using fallback callable"
            )
            return _local_fetch
    else:
        return _local_fetch


def _exec_code(code: str, timeout: int = 5):
    """Run a Python snippet in a subprocess and capture output."""
    try:
        proc = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "timeout"}
    except Exception as e:
        logger.exception("Code execution failed")
        return {"returncode": -2, "stdout": "", "stderr": str(e)}


def create_code_execution_tool(
    name: str = "code_exec", description: str = "Execute small Python snippets"
):
    """Return a code-exec FunctionTool or a subprocess-based fallback."""
    if ADK_AVAILABLE:
        try:
            ft = FunctionTool(name=name, func=_exec_code, description=description)
            return ft
        except Exception:
            logger.exception(
                "Failed to create ADK FunctionTool for code_exec; using fallback callable"
            )
            return _exec_code
    else:
        return _exec_code


def create_adk_scanner_tool(scanner_func: Callable):
    """Wrap the scanner as an ADK FunctionTool when possible."""
    name = "analyze_html"
    description = (
        "Run deterministic accessibility checks on HTML string (html, url) -> dict"
    )
    return create_function_tool_py(scanner_func, name, description)


def create_adk_fixer_agent_from_instruction(
    instruction: str = "Suggest HTML fixes",
) -> Any:
    """Alias to `create_fixer_agent` kept for backward compatibility."""
    return create_fixer_agent(instruction)


def run_adk_flow(
    manager_agent: Any, scanner_tool: Any, fixer_agent: Any, sample_path: str
):
    """Run ADK flow or fallback to local scan+fix for a sample file."""
    prompt = f"Run accessibility audit for {sample_path} and return structured results."

    if ADK_AVAILABLE:
        try:
            runner = InMemoryRunner()
            # In ADK, tools should be attached to the agent definition. Here we
            # assume `manager_agent` knows about the tools or the runner will
            # supply them via tooling APIs. We call runner.run to demonstrate
            # the intended wiring. This requires proper ADK setup to work.
            manager_out = runner.run(manager_agent, prompt)
            return {"manager_output": manager_out}
        except Exception:
            logger.exception(
                "ADK InMemoryRunner run failed; falling back to local flow"
            )

    # Fallback: call scanner_tool and fixer_agent directly (scanner_tool may be raw func)
    try:
        # If scanner_tool is a FunctionTool from ADK it may be callable; otherwise it's a function
        if callable(scanner_tool):
            html = Path(sample_path).read_text(encoding="utf-8")
            scan = (
                scanner_tool(html, sample_path)
                if scanner_tool.__code__.co_argcount >= 2
                else scanner_tool(html)
            )
        else:
            html = Path(sample_path).read_text(encoding="utf-8")
            scan = {"issues": [], "summary": "scanner not callable"}
    except Exception:
        logger.exception("Scanner tool failed in fallback")
        scan = {"issues": [], "summary": "scanner error"}

    try:
        # Try calling fixer_agent.run with a single arg (scan). If the agent
        # expects a different signature it may raise; we try a few fallbacks.
        if hasattr(fixer_agent, "run"):
            try:
                fixes = fixer_agent.run(scan)
            except TypeError:
                try:
                    fixes = fixer_agent.run(scan, html)
                except Exception:
                    fixes = fixer_agent.run(str(scan))
        elif callable(fixer_agent):
            fixes = fixer_agent(scan, html)
        else:
            fixes = []
    except Exception:
        logger.exception("Fixer agent failed in fallback")
        fixes = []

    # Normalize fixes to a list for predictable downstream processing
    if isinstance(fixes, str):
        fixes = [fixes]
    if fixes is None:
        fixes = []

    return {"manager_output": None, "scan": scan, "fixes": fixes}


def create_manager_agent(instruction: str = "Orchestrate accessibility audits") -> Any:
    """Return an ADK LlmAgent or a small fallback manager."""
    if ADK_AVAILABLE:
        # Configure a simple Gemini-backed LlmAgent — consumer must set API key.
        try:
            model = Gemini(model_name="gemini-2.5-flash-lite")
            agent = LlmAgent(
                name="access_manager",
                instruction=instruction,
                model=model,
            )
            return agent
        except Exception:
            logger.exception("Failed to create LlmAgent; using fallback manager")

    # Fallback manager
    class FallbackManager:
        def __init__(self, instr: str):
            self.instruction = instr

        def run(self, prompt: str, **kwargs):
            # Very small heuristic: echo a structured response for the demo
            return f"Fallback manager: would orchestrate for prompt: {prompt}"

    return FallbackManager(instruction)


def create_fixer_agent(instruction: str = "Suggest HTML fixes") -> Any:
    """Return an LLM fixer agent or simple fallback fixer."""
    if ADK_AVAILABLE:
        try:
            model = Gemini(model_name="gemini-2.5-flash-lite")
            agent = LlmAgent(
                name="fixer_agent",
                instruction=instruction,
                model=model,
            )
            return agent
        except Exception:
            logger.exception("Failed to create LlmAgent fixer; using fallback")

    class FallbackFixer:
        def __init__(self, instr: str):
            self.instruction = instr

        def run(self, prompt: str, **kwargs):
            return "Fallback fixer: suggest manual review or add alt attributes."

    return FallbackFixer(instruction)


def run_with_runner(agent, prompt: str):
    """Run an agent with ADK runner when available, otherwise call `run`."""
    if ADK_AVAILABLE:
        try:
            runner = InMemoryRunner()
            return runner.run(agent, prompt)
        except Exception:
            logger.exception("ADK runner failed; calling agent.run directly")

    # Fallback: call agent.run or agent(prompt)
    if hasattr(agent, "run"):
        return agent.run(prompt)
    elif callable(agent):
        return agent(prompt)
    else:
        return str(agent)


def create_session_service():
    """Return a session service (ADK-backed or simple in-memory fallback)."""
    if ADK_AVAILABLE:
        try:
            from google.adk.sessions import InMemorySessionService

            return InMemorySessionService()
        except Exception:
            logger.exception(
                "Failed to create ADK InMemorySessionService; using fallback"
            )

    # Fallback implementation
    class FallbackSessionService:
        def __init__(self):
            self._sessions: Dict[str, list] = {}

        def create_session(self, session_id: str) -> None:
            if session_id not in self._sessions:
                self._sessions[session_id] = []

        def append_event(self, session_id: str, event: Any) -> None:
            self.create_session(session_id)
            self._sessions[session_id].append(event)

        def get_events(self, session_id: str) -> list:
            return list(self._sessions.get(session_id, []))

    return FallbackSessionService()


def create_memory_service():
    """Return a memory service (ADK-backed or simple in-memory fallback)."""
    if ADK_AVAILABLE:
        try:
            from google.adk.memory import InMemoryMemoryService

            return InMemoryMemoryService()
        except Exception:
            logger.exception(
                "Failed to create ADK InMemoryMemoryService; using fallback"
            )

    class FallbackMemoryService:
        def __init__(self):
            self._store: Dict[str, Any] = {}

        def write(self, key: str, value: Any) -> None:
            self._store[key] = value

        def read_all(self) -> Dict[str, Any]:
            return dict(self._store)

        def query(self, predicate: Callable[[str, Any], bool]) -> Dict[str, Any]:
            return {k: v for k, v in self._store.items() if predicate(k, v)}

    return FallbackMemoryService()


def create_google_search_stub(name: str = "google_search", description: str = "Search web (stub)"):
    """Return a very small google_search callable or ADK FunctionTool stub.

    The stub accepts a query string and returns an empty list. This is
    sufficient for demo wiring and tests; real integration requires API keys.
    """
    def _stub(query: str):
        # Return an empty result list to keep demos deterministic
        return []

    if ADK_AVAILABLE:
        try:
            ft = FunctionTool(name=name, func=_stub, description=description)
            return ft
        except Exception:
            logger.exception("Failed to create ADK FunctionTool for google_search; using stub")
            return _stub
    else:
        return _stub
