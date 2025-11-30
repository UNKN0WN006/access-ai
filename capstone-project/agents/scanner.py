"""Scanner: deterministic accessibility checks (alt, headings, labels, ARIA, contrast).
This module is intentionally small and dependency-free for the demo.
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import re


def _hex_to_rgb(hex_str: str):
    hex_str = hex_str.strip()
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]
    if len(hex_str) == 3:
        hex_str = ''.join([c*2 for c in hex_str])
    if len(hex_str) != 6:
        return None
    try:
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return (r, g, b)
    except Exception:
        return None


def _relative_luminance(rgb):
    # sRGB to linear
    def channel(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(rgb1, rgb2):
    l1 = _relative_luminance(rgb1)
    l2 = _relative_luminance(rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def analyze_html(html: str, url: str = "") -> Dict[str, Any]:
    """Return a structured list of issues found in the HTML.

    Example return:
    {
        'issues': [ {'id':'alt_missing','element':'img','message':'img missing alt', 'selector':'img:nth-of-type(1)'} ],
        'summary': '2 issues found',
    }
    """
    soup = BeautifulSoup(html, 'html.parser')
    issues: List[Dict[str, Any]] = []

    # Check images for alt text
    for i, img in enumerate(soup.find_all('img')):
        alt = img.get('alt')
        if not alt or alt.strip() == '':
            issues.append({
                'id': 'alt_missing',
                'element': 'img',
                'message': 'Image missing alt text',
                'selector': f'img:nth-of-type({i+1})',
            })

    # Heading order / presence
    headings = [h.name for h in soup.find_all(['h1','h2','h3','h4','h5','h6'])]
    if headings and headings[0] != 'h1':
        issues.append({
            'id': 'heading_structure',
            'element': 'headings',
            'message': 'Document should start with an H1',
            'selector': headings[:3],
        })

    # Labels for inputs
    for inp in soup.find_all(['input','textarea','select']):
        _id = inp.get('id')
        aria_label = inp.get('aria-label')
        if _id:
            label = soup.find('label', attrs={'for': _id})
            if not label and not aria_label:
                issues.append({
                    'id': 'label_missing',
                    'element': 'input',
                    'message': f'Form control with id "{_id}" missing label or aria-label',
                    'selector': f'#{_id}',
                })
        else:
            # if no id, allow aria-label as alternative
            aria_label2 = inp.get('aria-label')
            if not aria_label2:
                issues.append({
                    'id': 'label_missing_id',
                    'element': 'input',
                    'message': 'Form control missing id so label cannot be associated and missing aria-label',
                    'selector': str(inp)[:80],
                })

    # ARIA checks: anchors with empty text should have aria-label or title
    for a in soup.find_all('a'):
        href = a.get('href')
        if href:
            text = a.get_text(strip=True)
            if not text:
                if not a.get('aria-label') and not a.get('title'):
                    issues.append({
                        'id': 'aria_label_missing',
                        'element': 'a',
                        'message': 'Anchor with no text should have aria-label or title',
                        'selector': str(a)[:80],
                    })

    # Simple color contrast heuristic: look for inline style with color and background-color
    for el in soup.find_all(True):
        style = el.get('style')
        if style and ('color' in style or 'background-color' in style):
            # crude parse for hex colors
            m_color = re.search(r'color\s*:\s*(#[0-9a-fA-F]{3,6})', style)
            m_bg = re.search(r'background-color\s*:\s*(#[0-9a-fA-F]{3,6})', style)
            if m_color and m_bg:
                rgb1 = _hex_to_rgb(m_color.group(1))
                rgb2 = _hex_to_rgb(m_bg.group(1))
                if rgb1 and rgb2:
                    try:
                        ratio = _contrast_ratio(rgb1, rgb2)
                        # WCAG AA for normal text requires 4.5:1
                        if ratio < 4.5:
                            issues.append({
                                'id': 'color_contrast_low',
                                'element': el.name,
                                'message': f'Low color contrast (ratio {ratio:.2f})',
                                'selector': str(el)[:80],
                            })
                    except Exception:
                        pass

    return {
        'issues': issues,
        'summary': f'{len(issues)} issue(s) found',
    }
