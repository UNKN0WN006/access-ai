import sys
from pathlib import Path

# ensure package path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents import fixer as fixer_mod
from agents import scanner as scanner_mod
from agents.patcher import apply_patch_to_html


def load_sample(name: str) -> str:
    return (Path(__file__).parent.parent / 'data' / 'sample_pages' / name).read_text(encoding='utf-8')


def test_sequential_patches_until_fixed():
    html = load_sample('medium.html')
    cur = html
    before = scanner_mod.analyze_html(cur, '')
    assert len(before.get('issues', [])) > 0

    max_iters = 10
    for i in range(max_iters):
        scan = scanner_mod.analyze_html(cur, '')
        if not scan.get('issues'):
            break
        # get suggestions from fixer for the current html
        suggestions = fixer_mod.suggest_fixes(scan, cur, tools={'scanner': scanner_mod.analyze_html})
        assert suggestions, 'No suggestions produced during sequential patching'
        # apply the first suggestion's patch
        s = suggestions[0]
        cur = apply_patch_to_html(cur, s.get('issue', {}), s.get('patch', ''))

    final = scanner_mod.analyze_html(cur, '')
    # Expect no remaining issues for the medium sample with our heuristics
    assert not any(True for _ in final.get('issues', [])), f'Remaining issues: {final.get("issues")} '
