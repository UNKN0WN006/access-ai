# fraudshield-workforce — AccessAI

AccessAI is a project that demonstrates a small multi-agent system which inspects HTML pages, highlights common accessibility issues (missing alt text, unlabeled form fields, problematic heading structure, etc.), and proposes conservative, explainable fixes.

The project is designed as a reproducible demo that can be run locally or on Kaggle without cloud API keys. Optional ADK/Gemini integrations are present but the code falls back to in-memory implementations so the demo remains self-contained.

What you'll find here
- `capstone-project/` — the main project (demo, agents, tests, and sample pages)
- `capstone-project/AccessAI_notebook.ipynb` — a notebook intended for the Kaggle submission
- `capstone-project/agents/` — Manager, Scanner, Fixer, and Patcher code
- `capstone-project/data/` — a few sample HTML pages I used for testing
- `capstone-project/tests/` — unit tests, sequential tests, and fuzz checks

Quick start (run locally)

I recommend Python 3.10+ and a virtual environment. From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
```

Then run the demo (offline mode):

```bash
python -m capstone-project.run_accessai
# or
python capstone-project/run_accessai.py
```

The script will scan the sample pages in `capstone-project/data/`, print the issues it finds, suggest fixes, and (when possible) re-scan to show whether the suggestions lowered the issue count.

Running tests

To run the project's tests:

```bash
python -m pytest capstone-project/tests -q
```

There's a GitHub Actions workflow in `.github/workflows/ci.yml` that runs these checks automatically.

How the code is organized (short)
- `manager.py`: wires the agents together and runs the demo flow
- `scanner.py`: simple, deterministic heuristics using BeautifulSoup
- `fixer.py`: creates conservative fix suggestions and verifies them
- `patcher.py`: small helpers that apply minimal HTML edits

Design notes (short and honest)
- Offline-first so judges or reviewers don't need API keys.
- Fixes are intentionally conservative and explainable — I avoid big rewrites.
- Tests drive the behavior: unit tests and some fuzzing help catch regressions.

Preservation and archives

The capstone itself lives in `capstone-project/` and has been preserved. I also moved old notes into a recovery branch named `archive/before-cleanup-2025-12-01` (you can find `archive/kaggle` and `archive/personal` there). I left all the important files in place so nothing gets accidentally removed.'

License

See `LICENSE` at the repository root.

Thanks for checking out the project — happy to write it.
