#!/usr/bin/env python3
"""
fix_loconotion.py  –  fixes scroll + centering on a loconotion-generated page.

Usage:
    python fix_loconotion.py <path/to/index.html>

Example:
    python fix_loconotion.py dist/the-bet-on-world-models/index.html
"""

import sys, re

# ── tweak these ──────────────────────────────────────────────────────────────
MAX_WIDTH    = "900px"
SIDE_PADDING = "48px"
# ─────────────────────────────────────────────────────────────────────────────


def fix(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    print(f"\nPatching: {path}\n")

    # 1. viewport ─────────────────────────────────────────────────────────────
    before = html
    html = re.sub(r",?maximum-scale=\d+", "", html)
    html = re.sub(r",?user-scalable=no",  "", html)
    print("✓ viewport" if html != before else "· viewport – already clean")

    # 2. notion-frame width (1920px → 100%) ───────────────────────────────────
    before = html
    html = re.sub(
        r'(class="notion-frame"[^>]*style="[^"]*?)width:\s*\d+px',
        r'\g<1>width: 100%',
        html,
    )
    print("✓ notion-frame width" if html != before else "· notion-frame width – already ok")

    # 3. notion-frame height (calc viewport-lock → auto) ──────────────────────
    before = html
    html = re.sub(
        r'(class="notion-frame"[^>]*style="[^"]*?)height:\s*calc\([^;]+\)',
        r'\g<1>height: auto',
        html,
    )
    print("✓ notion-frame height" if html != before else "· notion-frame height – already ok")

    # 4. notion-page-content: patch inline style directly ─────────────────────
    marker = 'class="notion-page-content"'
    idx = html.find(marker)
    if idx != -1:
        tag_start = html.rfind("<", 0, idx)
        tag_end   = html.find(">", idx) + 1
        tag = html[tag_start:tag_end]
        m = re.search(r'style="([^"]*)"', tag)
        if m:
            s = m.group(1)
            s = re.sub(r'\bwidth:\s*100%',     f'width: {MAX_WIDTH}',    s, count=1)
            s = re.sub(r'\bmax-width:\s*100%', f'max-width: {MAX_WIDTH}', s)
            s = re.sub(r'\bflex-grow:\s*\w+',   'flex-grow: 0',           s)
            s = re.sub(r'\bpadding-inline:[^;]+;?', '', s)
            s = s.rstrip("; ") + (
                f"; margin-left: auto; margin-right: auto;"
                f" padding-left: {SIDE_PADDING}; padding-right: {SIDE_PADDING};"
                f" box-sizing: border-box;"
            )
            new_tag = tag[:m.start(1)] + s + tag[m.end(1):]
            html = html[:tag_start] + new_tag + html[tag_end:]
            print(f"✓ notion-page-content – centered (max-width:{MAX_WIDTH} padding:{SIDE_PADDING})")
    else:
        print("✗ notion-page-content – not found!")

    # 5. MutationObserver to stop JS re-locking scroll ────────────────────────
    OBS = "loconotion-scroll-observer"
    if OBS not in html:
        script = (
            f'\n<script>/* {OBS} */'
            '(function(){'
            'function u(){'
            "['overflow','overflowX','overflowY'].forEach(function(p){"
            "var h=document.documentElement,b=document.body;"
            "if(['hidden','clip'].includes(h.style[p]))h.style[p]='';"
            "if(['hidden','clip'].includes(b.style[p]))b.style[p]='';"
            '});}'
            "new MutationObserver(u).observe(document.documentElement,{attributes:true,attributeFilter:['style']});"
            "new MutationObserver(u).observe(document.body,{attributes:true,attributeFilter:['style']});"
            'u();'
            '})();\n</script>'
        )
        html = html.replace("</body>", script + "</body>", 1)
        print("✓ scroll observer injected")
    else:
        print("· scroll observer – already present")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print("\nDone.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    fix(sys.argv[1])
