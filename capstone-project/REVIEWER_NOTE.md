# Reviewer Quick Start — AccessAI v1.0.0

This repository snapshot matches the `v1.0.0` release. Quick instructions for reviewers.

- **Release assets:** see the GitHub release `v1.0.0` for:
  - `AccessAI_notebook_executed.ipynb` (executed notebook for Kaggle reviewers)
  - `capstone-project-v1.0.0.zip` (zip of `capstone-project/`)

- **Patched outputs:** example patched HTML files are in `capstone-project/tmp/`.

- **Quick run (local):**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
python capstone-project/run_demo.py
```

`run_demo.py` launches a small offline demo that scans the sample pages and writes patched outputs to `capstone-project/tmp/`.

- **Run the test suite:**

```bash
pytest -q capstone-project/tests
```

- **Notes:**
  - `.venv/` is intentionally ignored by `.gitignore`.
  - If you need the raw notebook, use `AccessAI_notebook_executed.ipynb` from the release assets.
  - For questions, see `AUTHORS.md` and `ACKNOWLEDGMENTS.md`.

Thank you for reviewing AccessAI.
