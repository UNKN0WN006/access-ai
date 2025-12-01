# AccessAI — Automated Accessibility Auditor

AccessAI is a small, reproducible system that inspects HTML pages to find common accessibility issues and suggests minimal, explainable fixes. The project emphasizes deterministic heuristics and a verify-and-report workflow so results are transparent and easy to reproduce. The pipeline consists of a Scanner that reports issues, a Fixer that proposes conservative patches, a Patcher that applies small edits, and a Manager that runs verification scans. Everything runs locally without cloud API keys by default, though optional integrations are present for extended experiments. This writeup summarizes design choices, implementation details, evaluation approach, and how to run the demo for reviewer inspection.

## Introduction

Web accessibility remains an important but often overlooked part of software quality. Many websites suffer from low-hanging problems—images without alternative text, form controls without labels, inconsistent or missing headings, and insufficient contrast—that substantially degrade user experience for people with disabilities. The goal of AccessAI is to demonstrate how a focused, transparent automation approach can surface those issues reliably and suggest minimal, verifiable fixes. The project targets the intersection of usefulness and safety: suggestions should be easy to review, unlikely to break layouts, and simple for developers to accept or modify. To make the demonstration practical for reviewers and judges, the implementation favors deterministic heuristics over opaque machine learning models, and it includes a clear verification loop that measures issue reduction after patches are applied. The writeup documents the agents, the evaluation methodology, implementation trade-offs, and directions for future work. Readers should find concrete instructions to reproduce results locally or on Kaggle, along with a test suite that exercises the core behaviors. The repository includes sample pages, unit and fuzz tests, and a notebook that walks through the demo, so reviewers can verify the system without external services.

## Design and Agents

AccessAI organizes responsibilities into concise agents so each component remains easy to reason about. The Scanner performs syntactic and heuristic checks on the DOM, enumerating issues in categories such as `alt_missing`, `label_missing`, `heading_structure`, `aria_missing`, and `contrast_low`. For images the Scanner checks for present `alt` attributes and reports missing or suspiciously short values; for form controls it looks for associated `<label>` elements or `id`/`for` relationships and for nearby descriptive text. Heading analysis inspects heading depths to flag missing top-level headings or abrupt jumps. Contrast checks compute a simplified relative luminance ratio for inline styles or element attributes; the code is conservative to reduce false positives. The Fixer translates Scanner findings into small, reversible proposals. It produces a concise patch description, the target selector or element, the attribute change or wrapper to add, and a short human-readable explanation. The Patcher applies those edits to an in-memory copy of the HTML and outputs a unified diff for reviewer inspection. The Manager runs the full flow: baseline scan, proposals, patch application, and post-patch scan, and it summarizes per-category reductions. Each agent has limited responsibility which simplifies testing and makes it safe to run on many pages without extensive setup.

The design targets transparency: each suggestion shows its reasoning and confidence, and patches remain small. That makes it easy for a reviewer to accept or refine proposals. For generated alt-text, the system supplies templates and flags items for human review instead of applying them automatically. Diffs appear with the original HTML for easy context view.

## Implementation

The implementation is intentionally simple so reviewers can follow the code path from input to verification. The project uses Python 3 and BeautifulSoup for parsing; the default parser avoids external C dependencies to improve portability. The codebase separates concerns with small modules and functions, keeps public APIs minimal, and includes lightweight documentation and examples in the notebook. Contrast checks compute relative luminance using sRGB formulas and apply a conservative threshold to avoid noisy alerts. For form labeling we prefer explicit `label` associations and only fall back to `aria-label` or nearest-text heuristics when the label is genuinely missing. Patches are applied to an in-memory copy and written as minimal diffs which are displayed alongside the original content for manual inspection. Optional ADK tool wrappers exist to demonstrate how an LLM-assisted flow might be added, but they are disabled by default and require explicit credentials. Dependency management is handled via a `requirements.txt` file so judges can install dependencies in a virtual environment.

The repository includes unit tests that target specific heuristics and scenarios. Fuzz tests run randomized malformed HTML to ensure the scanner and patcher do not crash on inputs. When useful, the code uses pure-Python implementations to keep execution environments consistent.

## Evaluation

Evaluation focuses on reproducibility and clear metrics. For each sample page the Scanner reports counts by category rather than attempting to aggregate subjective severity scores. The categories include missing image alternatives, unlabeled inputs, problematic heading patterns, missing ARIA attributes, and low contrast. The Fixer applies patches on a temporary copy and the Manager re-runs the Scanner to compute post-patch counts. The primary evaluation metric is the per-category reduction; we also report the total change across all categories for convenience. Tests exercise specific templates (for example, adding an `alt` attribute) and sequential applications where patches are applied repeatedly until no further suggestions remain. Fuzz tests generate slightly corrupted HTML to ensure the scanner and patcher do not crash and to surface edge cases. The project includes a small set of representative sample pages: simple pages with images, forms, and navigation, plus a few medium-complexity examples. For judges who want to reproduce the evaluation, the notebook contains a cell-by-cell demonstration that runs the scan, applies patches, and prints before/after counts and diffs. Output is logged and saved so results can be audited later by stakeholders.

## Results and Discussion

The sample pages included with AccessAI illustrate typical outcomes and trade-offs. In most cases the Scanner identifies missing alt attributes and unlabeled inputs; small attribute-level patches reduce the counts for these categories reliably. Because fixes avoid structural rewrites, visual layout remains unchanged in almost all cases, which reduces reviewer burden and increases acceptance likelihood. The system also surfaces edge cases where automatic repairs are inappropriate: decorative images that should have empty alt attributes but lack clear context, or complex form widgets where an ARIA role needs careful human consideration. In those situations AccessAI records the finding and suggests a human review instead of applying an automatic change. The conservative approach reduces false positives and provides a safe starting point for developers who want automated assistance without handing over full editorial control. Anecdotally, reviewers found that the unified diffs and short explanations made it easy to scan suggested edits and accept them quickly. Overall, the tool is best viewed as a helper that surfaces low-effort, high-value issues, and it is most effective when paired with a short manual review step. Future user studies could quantify time savings and acceptance rates for suggested fixes in realistic workflows. This will guide improvements rapidly.

## Limitations and Future Work

AccessAI is intentionally focused, which leads to strengths and limitations. The heuristic approach makes the system predictable and easy to inspect but means it will miss complex semantics that a human reviewer or an advanced model might catch. Contrast evaluation is simplified and does not fully model CSS cascades or background images; improving this requires parsing style rules and computed styles which increases complexity. Another limitation is that automated alt-text generation is presently out of scope: generating rich, context-aware descriptions reliably requires a human-in-the-loop design. Future work therefore emphasizes augmenting the existing pipeline with optional, reviewable suggestions: better CSS-aware contrast checks, a human-assisted alt-text suggestion component, and a lightweight review interface that shows diffs and allows batch acceptance. Research directions could explore how much developer time is saved by this workflow and whether acceptance rates increase when diffs are small and explanations are clear. This roadmap balances automation and review.

## How to run

Set up a virtualenv, install requirements, and run the demo. Example commands are in the README and notebook.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r capstone-project/requirements.txt
```

The typical sequence installs dependencies, runs `python -m capstone-project.run_accessai` to scan included pages, and uses `pytest capstone-project/tests` to validate behavior. Inspect diffs and logs for verification. Use the notebook for step-by-step reproduction.

## Conclusion

AccessAI demonstrates that focused, explainable automation can assist developers and reviewers in finding and fixing straightforward accessibility issues. By keeping suggestions small and verifiable, the system reduces the friction of adopting automated help while preserving human oversight. The codebase emphasizes clarity, testability, and reproducibility: reviewers can run the notebook or scripts, inspect unified diffs, and confirm measurable improvements. This design makes the project suitable as a teaching tool, a lightweight reporting aid, or a pre-commit check that surfaces low-effort fixes before they reach production. It is not a replacement for comprehensive accessibility audits, but it does reduce the amount of manual work required to catch common oversights. I welcome feedback and collaboration to expand the dataset, refine heuristics, and add a small review UI. If you want a formatted PDF version, `writeup.tex` is included; I can compile it to PDF for distribution on request. Many thanks.

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
