from bs4 import BeautifulSoup
from typing import Dict
import re


def apply_patch_to_html(html: str, issue: Dict, patch: str) -> str:
    """Apply a very small, heuristic patch to an HTML string.

    This intentionally limited function supports the following demo ops:
      - add `alt` to `img:nth-of-type(N)` or first missing alt
      - insert a top-level `<h1>` at the start of `<body>`
      - insert a `<label for="id">Label</label>` before an input when possible
      - set `aria-label` on first unlabeled input as a fallback

    Returns the modified HTML (or original if no change applied).
    """
    soup = BeautifulSoup(html, 'html.parser')

    if issue.get('id') == 'alt_missing':
        sel = issue.get('selector', '')
        m = re.search(r'img:nth-of-type\((\d+)\)', sel)
        if m:
            idx = int(m.group(1)) - 1
            imgs = soup.find_all('img')
            if 0 <= idx < len(imgs):
                if not imgs[idx].get('alt'):
                    imgs[idx]['alt'] = 'Describe image'
                    return str(soup)
        # fallback: add alt to first img without alt
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = 'Describe image'
                return str(soup)

    if issue.get('id') == 'heading_structure':
        body = soup.body
        if body:
            h1 = BeautifulSoup('<h1>Page title</h1>', 'html.parser')
            body.insert(0, h1)
            return str(soup)

    if issue.get('id') in ('label_missing', 'label_missing_id'):
        _id = None
        sel = issue.get('selector', '')
        m = re.search(r'#([A-Za-z0-9_-]+)', sel)
        if m:
            _id = m.group(1)
        if _id:
            target = soup.find(attrs={'id': _id})
            if target:
                label = soup.new_tag('label', **{'for': _id})
                label.string = 'Label'
                target.insert_before(label)
                return str(soup)
        # fallback: for first input without id or aria-label, set an aria-label
        for inp in soup.find_all(['input', 'textarea', 'select']):
            if not inp.get('aria-label') and not inp.get('id'):
                inp['aria-label'] = 'Label'
                label = soup.new_tag('label')
                label.string = 'Label'
                inp.insert_before(label)
                return str(soup)

    return html


__all__ = ['apply_patch_to_html']
