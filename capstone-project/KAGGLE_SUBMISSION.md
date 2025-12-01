Kaggle submission checklist and instructions
-----------------------------------------

This document explains how to prepare and run the AccessAI demo on Kaggle, and which files to include in the submission bundle.

Files to include
- `AccessAI_notebook_executed.ipynb` — the executed notebook located in the `capstone-project/` folder. This is the safest upload for Kaggle reviewers.
- `data/` — the `capstone-project/data/` folder containing the sample HTML pages used by the demo.
- `agents/` — the `capstone-project/agents/` package (the Scanner, Fixer, Patcher, and Manager code).
- `requirements.txt` — the `capstone-project/requirements.txt` file listing Python dependencies. Ensure this file is present in the uploaded files.
- Optional: `tmp/` — pre-generated patched HTML files (useful for reviewers who want to inspect outputs without re-running the notebook).

Recommended Kaggle kernel settings
- Kernel: Python (choose a 3.10+ environment if available)
- Internet: Disabled (the project is offline-first and does not require cloud API keys)

How to run on Kaggle (recommended minimal steps)
1. Create a new Kaggle Notebook and upload the `capstone-project/` folder contents.
2. In the first cell, install dependencies (if Kaggle does not already provide them):

```bash
!pip install -r capstone-project/requirements.txt
```

3. Open `AccessAI_notebook_executed.ipynb` (the executed copy) and run the cells (they should already be executed). If you prefer to re-run, execute cells top-to-bottom.

Local reproduction (development)
--------------------------------
From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
python -m capstone-project.run_accessai
```

This writes patched HTML into `capstone-project/tmp/` and prints a short summary of per-page score reductions.

Notes for reviewers
- The demo is intentionally conservative in its patches. Fix suggestions are explainable and small so reviewers can inspect the diffs.
- If you see any behavior that looks incorrect, open an issue in the repo or contact the author listed in `AUTHORS.md`.

Credits & authorship
- See `AUTHORS.md` and `ACKNOWLEDGMENTS.md` for contributor information and acknowledgments.

Good luck — thanks for reviewing the submission!
