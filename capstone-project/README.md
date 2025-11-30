AccessAI — Multi-Agent Accessibility Auditor

Short pitch
-------------
AccessAI is a small multi-agent system that automates web accessibility audits: it fetches pages, runs deterministic accessibility checks, uses an LLM for human-readable explanations and prioritized fixes, and stores audit summaries for reuse.

Why this project
---------------
- Demonstrates multi-agent design (manager + specialist agents).
- Uses custom tools, sessions & memory, observability and evaluation — matching Kaggle Capstone requirements.
- Quick to run in a Kaggle Notebook without cloud secrets.

Contents
--------
- `AccessAI_notebook.ipynb` — Kaggle-ready notebook with demo cells.
- `requirements.txt` — Python dependencies.
- `agents/` — agent skeletons (manager, scanner, fixer).
- `data/sample_pages/` — three sample HTML pages (good, medium, bad).

Quick start (Kaggle Notebook)
-----------------------------
1. Open `capstone-project/AccessAI_notebook.ipynb` in Kaggle or Jupyter.
2. Install requirements (first code cell). Do NOT add API keys to the notebook.
3. Run the demo cells: fetch -> scan -> explain -> suggest fixes.

Notes
-----
- This scaffold is an MVP focused on the Capstone submission requirements. After you verify it runs, I'll implement the multi-agent orchestration, session/memory wiring, evaluation tests, and the short demo video script.
