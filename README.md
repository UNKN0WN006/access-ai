# AccessAI — Multi-Agent Accessibility Auditor

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

Kaggle submission

 - **Executed notebook:** `capstone-project/AccessAI_notebook_executed.ipynb` is included and ready for upload to Kaggle. It contains the run used to generate the demo artifacts in `capstone-project/tmp/`.
 - **What to include on Kaggle:** the executed notebook above, the `capstone-project/data/` folder (sample pages), and `capstone-project/agents/` (the code). You can also include `capstone-project/tmp/` if you want the pre-generated patched HTML files to be visible to reviewers.
 - **Run notes (local / Kaggle):** Kaggle kernels vary in Python version; use a Python 3.10+ kernel. If you need a reproducible run on Kaggle, upload the executed notebook and the `capstone-project/` folder. In a live kernel, run the top cells to install any missing dependencies and then run the notebook cells in order.
 - **Repro command (local):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
python -m capstone-project.run_accessai
```

 - **Authorship & credits:** See `AUTHORS.md` and `ACKNOWLEDGMENTS.md` in the repo. The project is offline-first and contains clear, conservative fixes so reviewers can inspect diffs easily.

License

See `LICENSE` at the repository root.

Thanks for checking out the project — happy to write it.
