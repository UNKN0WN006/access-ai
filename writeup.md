---
# Title

AccessAI — Multi-Agent Accessibility Auditor

---

## Subtitle

Fast audits, human-readable fixes, and persistent memory for repeat scans.

---

## Card / Thumbnail Image

Add a thumbnail image to the Kaggle submission card that visually identifies the project (e.g. `assets/demo_thumbnail.png`). Include the image in the repository and select it when creating the Kaggle card.

---

## Submission Track

Agents for Good

---

## Media Gallery (Optional)

- YouTube demo (optional): <ADD_YOUTUBE_URL_HERE>

---

## Project Description (<1500 words)

AccessAI is a compact, reproducible multi-agent system that automates lightweight accessibility audits for HTML pages and proposes conservative, human-reviewable fixes. The project demonstrates a sequential multi-agent orchestration (Manager → Scanner → Fixer → Patcher), conservative deterministic checks for common accessibility issues (missing alt text, heading structure, unlabeled form controls, and simple contrast heuristics), and an evaluation layer that scores before/after results.

Why this matters: accessibility problems are widespread and often remain unaddressed because manual audits are time-consuming and require specialized knowledge. AccessAI reduces the time-to-insight by combining rule-based scanners with LLM-assisted explanations and fix suggestions, packaged in a portable notebook and a small offline demo.

What it contains:
- A Manager that orchestrates the audit flow and wires tools.
- A Scanner that runs deterministic accessibility checks and produces structured issues.
- A Fixer that produces conservative patch suggestions (HTML snippets or small edits) and an optional verification path.
- A Patcher that applies safe edits to sample pages for demonstration purposes.
- A lightweight session/memory mechanism to retain recent audits during a demo run.
- Tests and an evaluation module that score scans and verify fixes on curated sample pages.

How it runs (quick):
1. Clone the repository and run the offline demo with `python capstone-project/run_demo.py`.
2. The demo scans sample pages in `capstone-project/data/sample_pages/` and emits patched outputs to `capstone-project/tmp/`.
3. Open `capstone-project/AccessAI_notebook_executed.ipynb` to step through the notebook demonstration and reproduce the results.

Notes on model usage and safety: AccessAI is designed to run without API keys by default — LLM calls are optional and guarded by an API-key check. NEVER commit API keys. Use environment variables for any credentials.

---

## Attachments (what I'm submitting)

- GitHub Repository: https://github.com/UNKN0WN006/fraudshield-workforce (release: `release/capstone-v1`, tag `v1.0.0`)
- Kaggle Notebook (executed): `capstone-project/AccessAI_notebook_executed.ipynb` (also uploaded to the release assets)
- Submission ZIP: `capstone-project-v1.0.0.zip` (uploaded to release `v1.0.0`)

---

## How the project maps to the evaluation criteria

**Category 1 — The Pitch (30 points)**
- Core Concept & Value (15 pts): AccessAI addresses a clear social need: making web content more accessible. The multi-agent approach is central — the Manager coordinates specialized agents so that rule-based checks scale and LLMs (optionally) provide human-friendly explanations.
- Writeup (15 pts): this document articulates the problem, architecture, demo steps, and submission artifacts.

**Category 2 — The Implementation (70 points)**
- Technical Implementation (50 pts): the repository demonstrates at least three course concepts: a Multi-agent system (sequential Manager → Scanner → Fixer), Tools (custom `fetch_html` and `analyze_html` tools and a `code_exec` verification tool), and Agent Evaluation (scoring and unit tests in `capstone-project/tests/`). The code is documented with comments describing design and behavior. A local Flask demo (`capstone-project/webapp.py`) shows a runnable deployment path.
- Documentation (20 pts): the repo contains `README.md`, `REVIEWER_NOTE.md`, and this writeup. The notebook includes inline Markdown explanation for Kaggle reviewers.

**Bonus (up to 20 pts)**
- Effective Use of Gemini (5 pts): The project documents optional Gemini usage and includes a guarded adapter to call a Gemini-compatible model when an API key is provided. The demo runs without keys.
- Agent Deployment (5 pts): A local Flask demo and `run_demo.py` demonstrate deployment; additional Cloud Run instructions are included in the repo for reproducibility.
- YouTube Video (10 pts): include a short demo video (<3 minutes) in the Media Gallery.

---

## Submission checklist (for Kaggle writeup)

- [x] Title
- [x] Subtitle
- [ ] Card / Thumbnail Image (add to repo and select in Kaggle)
- [x] Submission Track: Agents for Good
- [ ] Media Gallery: add YouTube URL if available
- [x] Project Description (this document, <1500 words)
- [x] Attachments: GitHub repo, executed notebook, zip uploaded to release

---

## How to run locally (quick copy/paste)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
python capstone-project/run_demo.py
```

Run tests:

```bash
pytest -q capstone-project/tests
```

---

## Safety note

Do not include API keys or secrets in the repository. When using an LLM, set credentials via environment variables and use the provided guarded adapter to enable/disable model calls.

---

If you want, I can also produce a short 2–3 minute video script and a thumbnail image now. Let me know which extras to add before you submit.
