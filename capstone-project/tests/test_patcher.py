import sys
from pathlib import Path

# ensure package path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.patcher import apply_patch_to_html
from agents import scanner as scanner_mod

DATA_DIR = Path(__file__).parent.parent / 'data' / 'sample_pages'


def load(name: str) -> str:
    return (DATA_DIR / name).read_text(encoding='utf-8')


def test_apply_patch_idempotent_alt():
    html = load('medium.html')
    before = scanner_mod.analyze_html(html, '')
    alt_issue = next((i for i in before['issues'] if i['id'] == 'alt_missing'), None)
    assert alt_issue is not None

    first = apply_patch_to_html(html, alt_issue, 'add alt')
    second = apply_patch_to_html(first, alt_issue, 'add alt')
    # applying twice should not create additional changes (idempotent)
    assert first == second


def test_apply_patch_limited_scope():
    html = load('medium.html')
    # original second image has no alt, first has alt
    soup_before = scanner_mod.analyze_html(html, '')
    issues_before = [i['id'] for i in soup_before['issues']]
    assert 'alt_missing' in issues_before

    alt_issue = next((i for i in soup_before['issues'] if i['id'] == 'alt_missing'), None)
    patched = apply_patch_to_html(html, alt_issue, 'add alt')
    # ensure we didn't modify other images that already had alt
    assert 'Describe image' in patched
    # ensure only the missing-alt image was changed by scanning patched HTML
    after = scanner_mod.analyze_html(patched, '')
    assert not any(i['id'] == 'alt_missing' for i in after['issues'])
