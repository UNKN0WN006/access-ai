# AccessAI — Automated Accessibility Auditor

AccessAI is a compact multi-agent system that inspects HTML pages for common accessibility issues and proposes small, explainable fixes. The goal is not to replace manual auditing, but to provide a reproducible, offline-capable demo that shows how lightweight agents can find and verify simple accessibility improvements. The notebook and code in this repository run without cloud keys; optional integrations are present but disabled by default so reviewers can reproduce results easily.

## Motivation

Accessibility problems — missing image descriptions, unlabeled form fields, confusing heading structures — are common and often easy to miss during development. AccessAI focuses on issues that are high-impact for users and straightforward to detect or patch automatically. The project demonstrates how simple heuristics, transparent rules, and a short verification loop can produce conservative but useful suggestions.

## Approach

AccessAI splits the work into small, purpose-built agents:

- **Scanner**: parses HTML with BeautifulSoup and reports issues such as missing `alt` attributes, heading-sequence problems, inputs without `<label>`, missing `aria-*` attributes, and low-contrast color pairs found via a simple luminance-based check.
- **Fixer**: formats conservative, testable fix proposals — for example, add a short `alt` placeholder, insert a top-level heading if none exists, or attach an `aria-label` fallback for unlabeled controls.
- **Patcher**: applies minimal edits to HTML (attributes or small wrappers) without large rewrites.
- **Manager**: orchestrates Scanner → Fixer → Patcher, and re-runs the Scanner to verify whether suggested fixes reduce the reported issue counts.

Each suggestion includes a brief explanation and an intentionally conservative confidence estimate. Fixes avoid layout changes and focus on clarity and reversibility.

## Implementation notes

The demo is implemented in Python and relies on deterministic rules rather than heavy ML models. This keeps the behavior transparent and reproducible.

- Parsing: BeautifulSoup with the built-in `html.parser` for portability.
- Contrast: a simplified relative-luminance contrast ratio check; this is a practical demonstration rather than a full WCAG implementation.
- Tools: local `fetch_html` and `code_execution` wrappers keep the demo self-contained; optional ADK/Gemini integration is guarded so it is not required.

## Evaluation

Evaluation is deliberately simple: each sample page is scanned to produce baseline counts for categories such as `alt_missing`, `label_missing`, `heading_structure`, `aria_missing`, and `contrast_low`. The Fixer applies patches to a copy of the page and the Scanner runs again to compute post-patch counts. The reported reductions are easy to verify and reproducible.

Unit tests cover specific fix behaviors and fuzz-style tests feed malformed HTML to ensure robustness. The CI workflow runs the test suite to prevent regressions.

## Example observations

On the included sample pages AccessAI commonly finds missing alt attributes and unlabeled inputs; applying small attribute-based fixes reduces those counts in many cases. Every change is reported with the affected element and the before/after counts so reviewers can inspect the edits.

## How to run

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
```

2. Run the demo script (offline):

```bash
python -m capstone-project.run_accessai
```

3. Run tests:

```bash
python -m pytest capstone-project/tests -q
```

## Limitations and future work

Because the system uses heuristics it will miss nuanced accessibility problems. Future directions include integrating CSS-aware contrast checks, adding human-in-the-loop alt text suggestions, and expanding ARIA validation.

## Final notes

This writeup and the notebook aim to be easy to run and inspect. If you want a formatted two-column LaTeX version for printing or slides, see `writeup.tex` in this folder.
