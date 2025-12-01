import random
import sys
from pathlib import Path

# ensure package path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents import scanner as scanner_mod
from agents.patcher import apply_patch_to_html


def random_malformed_html(rng: random.Random) -> str:
    parts = []
    # random number of images
    n = rng.randint(0, 4)
    for i in range(n):
        if rng.random() < 0.5:
            parts.append(f'<img src="/img{i}.png" alt="ok"/>')
        else:
            parts.append(f'<img src="/img{i}.png"/>')
    # random inputs
    m = rng.randint(0, 3)
    for j in range(m):
        if rng.random() < 0.5:
            parts.append(f'<input id="f{j}" type="text"/>')
        else:
            parts.append('<input type="text"/>')

    # occasionally introduce broken fragments
    if rng.random() < 0.3:
        parts.append("<div><span>broken")
    if rng.random() < 0.2:
        parts.append('<a href="/x"></a>')

    # shuffle and join with possible missing closing tags
    rng.shuffle(parts)
    html = "<html><body>" + "".join(parts) + "</body></html>"
    # randomly truncate to simulate corruption
    if rng.random() < 0.2:
        cut = rng.randint(1, len(html))
        html = html[:cut]
    return html


def test_fuzz_malformed_inputs_no_crash_and_monotonic():
    rng = random.Random(0)
    trials = 200
    for _ in range(trials):
        h = random_malformed_html(rng)
        scan = scanner_mod.analyze_html(h, "")
        # ensure analyzer returns valid result
        assert isinstance(scan, dict)
        assert "issues" in scan

        # if there are issues, attempt to apply the first patch and ensure nothing crashes
        if scan.get("issues"):
            issue = scan["issues"][0]
            patched = apply_patch_to_html(h, issue, "patch")
            post = scanner_mod.analyze_html(patched, "")
            assert isinstance(post, dict)
            assert "issues" in post
            # Monotonicity check: heuristic patch should not increase the number of issues
            assert len(post.get("issues", [])) <= len(scan.get("issues", [])), (
                "Number of issues increased after patch (heuristic should not worsen): "
                f'{len(scan.get("issues", []))} -> {len(post.get("issues", []))}'
            )
