# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.0] - 2025-12-01
### Added
- Completed AccessAI capstone demo: multi-agent offline-first demo (Manager, Scanner, Fixer, Patcher).
- `capstone-project/AccessAI_notebook_executed.ipynb` — executed notebook prepared for Kaggle submission.
- `capstone-project/KAGGLE_SUBMISSION.md` — Kaggle packaging and run instructions.
- `run_demo.py` — one-line runner to execute the offline demo from the repo root.
- `capstone-project/tmp/` patched HTML outputs for sample pages (pre-generated artifacts).

### Changed
- README updated with Kaggle submission notes and reproduction instructions.
- `capstone-project/requirements.txt` updated to include optional `ipywidgets` for notebook previews.

### Fixed
- Minor notebook fixes for robust repo-root resolution and non-interactive preview helper.

### Notes
- This release is intended for packaging and review on Kaggle and GitHub. The demo is offline-first; no cloud API keys are required to run the sample flow.
