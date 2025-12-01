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

- YouTube demo (optional): 

---

## Project Description (<1500 words)

### Problem Statement -- the problem you're trying to solve, and why you think it's an important or interesting problem to solve

Many websites contain accessibility defects (missing alt text, broken heading structure, unlabeled form controls, insufficient contrast) that prevent people with disabilities from using content effectively. Manual audits are slow, require specialist knowledge, and are rarely performed at scale. This project addresses a clear social and technical need: make basic accessibility auditing fast, repeatable, and actionable so teams can find and fix common issues earlier in the content lifecycle.

### Why agents? -- Why are agents the right solution to this problem

Agents let us separate responsibilities into specialized components: a Manager orchestrates workflow, a Scanner runs deterministic checks at scale, and a Fixer proposes safe, prioritized repairs. This modular approach is extensible, testable, and allows hybrid operation where deterministic logic ensures reliability while optional LLM-assisted agents provide human-friendly explanations and prioritized recommendations.

### What you created -- What's the overall architecture?

AccessAI is a sequential multi-agent system: Manager → Scanner → Fixer → Patcher. Key elements:
- Manager: wires tools and coordinates agent calls.
- Scanner: deterministic HTML checks (alt text, headings, labels, simple contrast heuristics) producing structured issues.
- Fixer: conservative patch suggestions (HTML snippets/diffs) and optional verification via a code-exec tool.
- Patcher: safely applies demo patches to sample pages.
- Tools: custom FunctionTools (`fetch_html`, `analyze_html`, `code_exec`) and a guarded adapter for optional LLM calls.
- Session/Memory: lightweight demo session store for short-term audit state.
- Observability/Evaluation: logging, unit tests, and a scoring module that quantifies before/after improvements.

Artifacts included in the release: an executed notebook (`capstone-project/AccessAI_notebook_executed.ipynb`), demo runner (`run_demo.py`), local Flask UI (`capstone-project/webapp.py`), unit tests (`capstone-project/tests/`), and sample patched outputs (`capstone-project/tmp/`).

### Demo -- Show your solution

Quick local steps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
python capstone-project/run_demo.py
```

What you will see:
- The Manager triggers the Scanner against sample pages in `capstone-project/data/sample_pages/`.
- The Scanner emits structured issues; the Fixer provides conservative HTML edits.
- Patched HTML is written to `capstone-project/tmp/` and may be inspected in a browser.
- Optional LLM explanations run only when an API key is provided; by default the demo runs offline.

Validate with tests:

```bash
pytest -q capstone-project/tests
```

### The Build -- How you created it, what tools or technologies you used

- Language & runtime: Python 3.x and Jupyter Notebook.
- Parsing & tooling: BeautifulSoup (`bs4`), `lxml`, `requests` for fetches, `Flask` for demo UI, and `pytest` for tests.
- Architecture: simple, modular agent modules under `capstone-project/agents/`, tools-as-dict wiring, and guarded adapters for optional LLM use.
- Design choices: deterministic rule checks provide repeatability; LLM calls are optional and gated by environment variables to avoid requiring credentials for reviewers.

### If I had more time, this is what I'd do

- Implement a richer InMemorySessionService and a small persistent memory bank for retrieving past audits (claim Sessions & Memory).
- Add a guarded LLM sub-agent (Gemini-compatible adapter) and a fallback mock to claim the Gemini bonus while preserving offline runs.
- Add parallel scanning (parallel agents) and a resumable long-running job for large-site crawls.
- Improve observability with structured logs and simple metrics (issue counts, fix rates) plus a basic dashboard.
- Provide a Cloud Run / Agent Engine deployment recipe and a 2–3 minute demo video with a thumbnail for the Kaggle card.

Notes: the project description above fits under 1500 words and is designed to be concise for the Kaggle writeup.

---

## Attachments (what I'm submitting)

- GitHub Repository: https://github.com/UNKN0WN006/AccessAI (release: `release/capstone-v1`, tag `v1.0.0`)
- Kaggle Notebook (executed): `capstone-project/AccessAI_notebook_executed.ipynb` (also uploaded to the release assets)
- Submission ZIP: `capstone-project-v1.0.0.zip` (uploaded to release `v1.0.0`)

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