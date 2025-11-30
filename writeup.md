Project name: AccessAI — Multi-Agent Accessibility Auditor (Track: Agents for Good)
Why it stands out:
Social impact (accessibility) — fits "Agents for Good".
Uses multi-agent patterns you learned: manager + specialist agents (parallel/ sequential).
Demonstrates at least 3 required ADK features: multi-agent, custom tools (HTML fetch + rule-check), Sessions & Memory (store audits), Observability (logging) and Evaluation (testcases). That covers scoring for Implementation and Bonus (you can use Gemini for one agent for +5 bonus).
Fast to build: you can demo with 3 sample pages and LLM-powered explanations + deterministic rule checks.
Project scope (minimum viable for 1 day)
Core features (MVP):
Manager agent (LLM) orchestrates audit requests.
Crawler/Fetcher tool: fetches HTML (FunctionTool).
Scanner agent: runs deterministic checks (alt attributes, heading order, color contrast heuristics) and calls LLM for explanations and prioritized fixes.
Fixer agent: suggests code snippets / diff-style fixes for top issues.
Session + Memory: store recent audits and retrieve past audits for the same site (demo reuse).
Observability: simple logging of each step (what tool called, observations).
Evaluation: include 3 sample pages and 4-6 unit tests that assert the scanner finds expected issues.
Bonus (time-permitting):
Use gemini-* model name in one sub-agent (documented but you can run on Kaggle if you have API key) to claim the Gemini bonus.
Short deployment docs or a Cloud Run instruction for bonus deploy points.
2.5–3 minute demo video.
One-day schedule (8–10 hours, tight but doable)
00:00–00:30 (30m) — Finalise idea, repo/notebook creation, collect sample pages.
00:30–01:45 (75m) — Implement repo skeleton + agent scaffolding (Manager + Scanner + Fixer) using ADK LlmAgent and FunctionTool placeholders.
01:45–03:15 (90m) — Implement HTML fetch tool + deterministic scanner rules (alt text, heading order, form labels, link text, simple color contrast using luminance approximations).
03:15–04:15 (60m) — Integrate LLM explanations + Fixer agent that returns suggested HTML snippets.
04:15–05:00 (45m) — Add Sessions & InMemoryMemory to store audit summaries; demo retrieval.
05:00–05:45 (45m) — Add logging and simple evaluation tests (assert expected issues found). Run tests and refine.
05:45–06:30 (45m) — Write README and Kaggle writeup draft (<=1500 words), architecture diagram (ASCII or quick PNG).
06:30–07:00 (30m) — Record video (scripted, 2–3 takes), upload, create thumbnail.
07:00–07:30 (30m) — Final polish, create submission attachments, verify no API keys, submit.
Concrete technical plan & ADK features mapping
Multi-agent: Manager (LLM) + Scanner (specialist rule-runner) + Fixer (LLM-assisted code suggester). Use SequentialAgent or a simple custom orchestration pattern.
Tools:
Built-in: google_search (optional for research)
Custom FunctionTool: fetch_html(url) — returns HTML string (use requests).
Custom FunctionTool: analyze_html(html) — runs deterministic checks.
Code execution tool for running small scripts (if needed).
Sessions & Memory:
InMemorySessionService to show per-run state.
InMemoryMemoryService for storing top-level audit summaries (per domain).
Observability:
Python logging capturing manager/tool events, write to logs/agent.log.
Evaluation:
*.test.json style or simple pytest file with test pages in data/.
Deployment (optional):
Provide Dockerfile or requirements.txt and simple instructions to run on Cloud Run or Kaggle Notebooks.
Minimal ADK agent skeleton (pseudo-ready snippet)
Use in your Kaggle notebook or repo. Replace secrets with environment variables (do NOT commit keys).
Python skeleton (short):

Manager agent coordinates:
Accepts a URL
Calls fetch_html tool
Calls ScannerAgent (synchronously via runner) to get issues and a summary
Calls FixerAgent for suggested code fixes for top N issues
Stores results in MemoryService and returns a report
Example (conceptual):

Manager: LlmAgent(name="access_manager", instruction="You orchestrate accessibility audits...")
fetch_html: FunctionTool that returns HTML
scanner_agent: LlmAgent or pure function tool that returns structured list of issues
fixer_agent: LlmAgent that generates code fixes
I can create a ready-to-run notebook cell with this skeleton if you want.

README / Kaggle writeup template (outline)
Title: AccessAI — Multi-Agent Accessibility Auditor
Subtitle: Fast audits, human-readable fixes, and persistent memory for repeat scans.
Problem: Accessibility is often ignored; manual audits are slow and inconsistent.
Solution: Multi-agent system that (1) fetches a page, (2) runs deterministic and LLM-assisted checks, (3) proposes code fixes and stores audits in memory.
Architecture: concise diagram and bullets (Manager, Fetcher, Scanner, Fixer, Memory, Tools).
How to run: (Kaggle notebook instructions + local requirements)
Files & Demo:
notebook.ipynb — interactive demo
agents/agent.py — agent definitions
data/sample_pages/ — sample HTML files
README.md — this doc
Scoring pick-ups:
Multi-agent + Tools + Sessions & Memory + Observability + Evaluation.
Video link & short bullet demo steps.
Short video script (60–180s)
0:00–0:10s — Title + one-sentence problem (why accessibility matters).
0:10–0:35s — Architecture (visual) and quick mention of ADK features.
0:35–1:30s — Live demo: run audit for example URL (show issues found and fix suggestions).
1:30–1:50s — Show memory retrieval of previous audit and logging/tracing.
1:50–2:00s — Impact statement + call to action / GitHub link.
Evaluation & scoring checklist (for judges)
Category 1 (Pitch): Clear problem + value statement + short metrics (time saved, number of issues found).
Category 2 (Implementation): Show code quality, multi-agent usage, tools, sessions/memory, and tests.
Bonus: Use Gemini (documented; run if possible), short video (<3min), and deployment docs for Cloud Run or Agent Engine.
Safety & submission notes
NEVER commit API keys. Use environment variables or Kaggle secrets.
Keep the Kaggle Notebook self-contained (sample pages + code) so judges can run it without cloud creds.
For Gemini bonus: document model usage and where to set API key. If you can include a short fallback mode (dummy LLM outputs) to let graders run the notebook without keys, it’s better.
Offer — next steps I can do immediately
I can:
Generate the repo/notebook scaffold (files: notebook.ipynb or kaggle/dayX/AccessAI.ipynb, agents/agent.py, data/sample_pages/, README.md, requirements.txt) for you right now.
Or produce the minimal Python code skeleton for the agents and a runnable Kaggle notebook JSON structure (per your notebook-format instructions).
Tell me which you want me to do next:
A) Create the scaffold repository + notebook (I will produce files and test-run quick unit tests), or
B) Produce the concise runnable Kaggle notebook JSON with code cells and markdown (so you can open & run it in Kaggle quickly), or
C) Just get you a compact implementation snippet + README + video script and you’ll proceed yourself.