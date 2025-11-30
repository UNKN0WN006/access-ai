import sys
from pathlib import Path

# ensure package path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.patcher import apply_patch_to_html
from agents import scanner as scanner_mod


def test_multiple_missing_alts_patches_one_at_a_time():
    html = """<html><body>
    <img src="/a.png" />
    <img src="/b.png" />
    <img src="/c.png" alt="ok" />
    </body></html>"""

    before = scanner_mod.analyze_html(html, '')
    missing = [i for i in before['issues'] if i['id'] == 'alt_missing']
    assert len(missing) == 2

    # Apply patch for the first missing-alt issue
    patched = apply_patch_to_html(html, missing[0], 'add alt')
    after = scanner_mod.analyze_html(patched, '')
    remaining = [i for i in after['issues'] if i['id'] == 'alt_missing']
    # Should have reduced by one
    assert len(remaining) == 1


def test_input_with_id_receives_label_for_id():
    html = """<html><body>
    <form>
      <input id="username" type="text" />
    </form>
    </body></html>"""

    before = scanner_mod.analyze_html(html, '')
    # Should detect missing label for id-based control
    assert any(i['id'] == 'label_missing' for i in before['issues'])

    issue = next(i for i in before['issues'] if i['id'] == 'label_missing')
    patched = apply_patch_to_html(html, issue, 'insert label')
    after = scanner_mod.analyze_html(patched, '')
    # The label_missing issue for that id should be gone
    assert not any(i['id'] == 'label_missing' for i in after['issues'])


def test_malformed_html_does_not_crash_and_gets_fixed():
    # missing closing tags, unusual nesting
    html = """<html><body><div><img src='/x.png'><form><input></body></html>"""
    before = scanner_mod.analyze_html(html, '')
    # There should be at least one alt_missing or label_missing_id reported
    assert any(i['id'] in ('alt_missing', 'label_missing_id', 'label_missing') for i in before['issues'])

    # Try to apply first found issue and ensure no crash and scanner returns
    issue = before['issues'][0]
    patched = apply_patch_to_html(html, issue, 'patch')
    after = scanner_mod.analyze_html(patched, '')
    assert isinstance(after, dict)
    assert 'issues' in after
