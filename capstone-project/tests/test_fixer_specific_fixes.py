import sys
from pathlib import Path

# Ensure package path matches other tests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents import scanner as scanner_mod
from agents import fixer as fixer_mod
from agents.patcher import apply_patch_to_html
from bs4 import BeautifulSoup


DATA_DIR = Path(__file__).parent.parent / 'data' / 'sample_pages'


def load(name: str) -> str:
    return (DATA_DIR / name).read_text(encoding='utf-8')


def _find_suggestion_for_issue(suggestions, issue_id):
    for s in suggestions:
        if s.get('issue', {}).get('id') == issue_id:
            return s
    return None


def test_medium_alt_missing_fixed():
    html = load('medium.html')
    before = scanner_mod.analyze_html(html, '')
    assert any(i['id'] == 'alt_missing' for i in before['issues'])

    suggestions = fixer_mod.suggest_fixes(before, html, tools={'scanner': scanner_mod.analyze_html})
    alt_sugg = _find_suggestion_for_issue(suggestions, 'alt_missing')
    assert alt_sugg is not None, 'Expected an alt_missing suggestion'
    # Verify the exact patch effect: applying the patch should add an alt attribute
    new_html = apply_patch_to_html(html, alt_sugg['issue'], alt_sugg['patch'])
    soup = BeautifulSoup(new_html, 'html.parser')
    # The fixer sets alt="Describe image" for the first missing alt
    assert any(img.get('alt') == 'Describe image' for img in soup.find_all('img')), 'No alt="Describe image" found after patch'
    # Ensure post-scan no longer contains the alt_missing issue
    post = alt_sugg.get('post_scan') or scanner_mod.analyze_html(new_html, '')
    assert not any(i.get('id') == 'alt_missing' for i in post.get('issues', [])), 'alt_missing still present after patch'


def test_medium_heading_added():
    html = load('medium.html')
    before = scanner_mod.analyze_html(html, '')
    assert any(i['id'] == 'heading_structure' for i in before['issues'])

    suggestions = fixer_mod.suggest_fixes(before, html, tools={'scanner': scanner_mod.analyze_html})
    h_sugg = _find_suggestion_for_issue(suggestions, 'heading_structure')
    assert h_sugg is not None, 'Expected a heading_structure suggestion'
    # Verify the exact patch effect: applying the patch should insert an H1
    new_html = apply_patch_to_html(html, h_sugg['issue'], h_sugg['patch'])
    soup = BeautifulSoup(new_html, 'html.parser')
    # Expect an H1 element present in the body
    assert soup.body.find('h1') is not None, 'No <h1> inserted by heading patch'
    post = h_sugg.get('post_scan') or scanner_mod.analyze_html(new_html, '')
    assert not any(i.get('id') == 'heading_structure' for i in post.get('issues', [])), 'heading_structure still present after patch'


def test_bad_label_missing_id_fixed():
    html = load('bad.html')
    before = scanner_mod.analyze_html(html, '')
    assert any(i['id'] == 'label_missing_id' for i in before['issues'])

    suggestions = fixer_mod.suggest_fixes(before, html, tools={'scanner': scanner_mod.analyze_html})
    label_sugg = _find_suggestion_for_issue(suggestions, 'label_missing_id')
    assert label_sugg is not None, 'Expected a label_missing_id suggestion'
    # Verify the exact patch effect: applying the patch should set an aria-label
    new_html = apply_patch_to_html(html, label_sugg['issue'], label_sugg['patch'])
    soup = BeautifulSoup(new_html, 'html.parser')
    # The fixer sets aria-label="Label" on the first unlabeled input
    found = False
    for inp in soup.find_all(['input', 'textarea', 'select']):
        if inp.get('aria-label') == 'Label':
            found = True
            break
    assert found, 'No input with aria-label="Label" found after patch'
    post = label_sugg.get('post_scan') or scanner_mod.analyze_html(new_html, '')
    assert not any(i.get('id') == 'label_missing_id' for i in post.get('issues', [])), 'label_missing_id still present after patch'
