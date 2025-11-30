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

from agents.manager import orchestrate
from agents.scanner import analyze_html
from agents.fixer import suggest_fixes
from agents.adk_wrappers import (
    create_function_tool_py,
    create_manager_agent,
    create_fixer_agent,
    run_with_runner,
    create_session_service,
    create_memory_service,
)

# New ADK-specific helpers (if ADK is present these return ADK objects)
from agents.adk_wrappers import create_adk_scanner_tool, create_adk_fixer_agent_from_instruction
from agents.adk_wrappers import run_adk_flow
from agents.adk_wrappers import create_fetch_html_tool
from agents.adk_wrappers import create_code_execution_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('accessai')

DATA_DIR = Path(__file__).parent / 'data' / 'sample_pages'


def demo_mode():
    logger.info('Running in demo (offline) mode using local functions')
    # Create lightweight session & memory services for the demo
    session_service = create_session_service()
    memory_service = create_memory_service()

    # Use the fetch_html tool so manager orchestration can call it uniformly.
    fetch_tool = create_fetch_html_tool()
    # Add a small code execution tool (demo only)
    code_exec = create_code_execution_tool()

    for sample in ['good.html', 'medium.html', 'bad.html']:
        path = DATA_DIR / sample
        # orchestrate expects tools dict with 'fetch_html' callable
        result = orchestrate(str(path), {'fetch_html': fetch_tool, 'scanner': analyze_html, 'fixer': suggest_fixes, 'code_exec': code_exec})
        # Store session events and memory summary
        session_id = f'audit:{sample}'
        session_service.create_session(session_id)
        session_service.append_event(session_id, {'stage': 'scan', 'summary': result['scan']['summary']})
        memory_key = f'memory:{sample}'
        memory_service.write(memory_key, {'url': str(path), 'summary': result['scan']['summary']})
        print('---')
        print('URL:', result['url'])
        print('Summary:', result['scan']['summary'])
        for issue in result['scan']['issues']:
            print('-', issue['message'])
        print('Suggestions:')
        for s in result['fixes']:
            print(' *', s['suggestion'])

    # Show stored memory content
    print('\nStored memory items:')
    all_mem = memory_service.read_all()
    for k, v in all_mem.items():
        print('-', k, '->', v)


def adk_mode():
    logger.info('Attempting ADK mode (requires google-adk and credentials)')
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
    sample = DATA_DIR / 'bad.html'
    adk_result = run_adk_flow(manager_agent, scanner_tool, fixer_agent, str(sample))

    if adk_result.get('manager_output') is not None:
        print('Manager output (ADK runner):')
        print(adk_result['manager_output'])
    else:
        scan = adk_result.get('scan')
        fixes = adk_result.get('fixes')
        print('\nScan summary:', scan.get('summary'))
        print('Fix suggestions:')
        for s in fixes:
            # s may be dict or text depending on fixer implementation
            if isinstance(s, dict):
                print('-', s.get('suggestion'))
            else:
                print('-', s)

    # Persist audit summary in memory
    memory_key = f'adk:bad.html'
    try:
        memory_service.write(memory_key, {'summary': scan['summary'], 'url': str(sample)})
        print('\nMemory written:', memory_key)
    except Exception:
        logger.exception('Failed to write memory')

    # Show session events (if any)
    try:
        session_service.create_session('adk-demo')
        session_service.append_event('adk-demo', {'action': 'scanned bad.html', 'summary': scan['summary']})
        print('\nSession events for adk-demo:', session_service.get_events('adk-demo'))
    except Exception:
        logger.exception('Session service calls failed')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['demo', 'adk'], default='demo')
    args = parser.parse_args()

    if args.mode == 'demo':
        demo_mode()
    else:
        adk_mode()


if __name__ == '__main__':
    main()
