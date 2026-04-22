#!/usr/bin/env python3
"""
Fix scrolling in loconotion-generated pages.
Run from the dist folder: python fix_scroll.py
"""

import os
import re
import sys

dist_dir = sys.argv[1] if len(sys.argv) > 1 else "."

# ── 1. Find the CSS files ────────────────────────────────────────────────────

html_file = os.path.join(dist_dir, "index.html")
if not os.path.exists(html_file):
    print(f"ERROR: No index.html found in '{dist_dir}'")
    sys.exit(1)

html = open(html_file).read()
css_files = re.findall(r'href="([^"]+\.css)"', html)
print(f"Found {len(css_files)} CSS files: {css_files}")

# ── 2. Fix: main Notion CSS (overflow:hidden + height:100vh) ─────────────────

MAIN_PATTERN = re.compile(
    r'(html\.notion-html,\s*body\.notion-body,\s*#notion-app\s*\{[^}]*\})',
    re.DOTALL
)
APP_INNER_PATTERN = re.compile(
    r'(\.notion-app-inner\s*\{\s*height:\s*100%\s*\})'
)

main_fixed = False
for css_name in css_files:
    css_path = os.path.join(dist_dir, css_name)
    if not os.path.exists(css_path):
        continue
    content = open(css_path).read()
    if MAIN_PATTERN.search(content):
        # Fix html/body/notion-app block
        content = MAIN_PATTERN.sub(
            "html.notion-html, body.notion-body, #notion-app {\n"
            "    min-height: 100vh;\n"
            "    position: relative;\n"
            "    overflow: auto\n"
            "    }",
            content
        )
        # Fix notion-app-inner height
        content = APP_INNER_PATTERN.sub(
            ".notion-app-inner {\n    height: auto\n    }",
            content
        )
        open(css_path, "w").write(content)
        print(f"✓ Fixed overflow:hidden in {css_name}")
        main_fixed = True
        break

if not main_fixed:
    print("WARNING: Could not find the main Notion CSS block to fix.")

# ── 3. Fix: loconotion custom CSS (notion-frame + notion-scroller) ───────────

LOCONOTION_CSS = "e1d809d762eeca23edf0cb31bb17bf3c703085f5.css"
loconotion_path = os.path.join(dist_dir, LOCONOTION_CSS)

FRAME_PATTERN = re.compile(
    r'(/\* stops inline databases from overflowing horizontally \*/\s*'
    r'\.notion-frame\s*\{[^}]*\})',
    re.DOTALL
)

if os.path.exists(loconotion_path):
    content = open(loconotion_path).read()
    if FRAME_PATTERN.search(content):
        content = FRAME_PATTERN.sub(
            "/* stops inline databases from overflowing horizontally */\n"
            ".notion-frame {\n"
            "  max-width: 100%;\n"
            "  width: 100vw !important;\n"
            "  height: auto !important;\n"
            "  min-height: calc(100vh - 44px) !important;\n"
            "}\n\n"
            ".notion-scroller.vertical {\n"
            "  overflow-y: auto !important;\n"
            "  height: auto !important;\n"
            "}",
            content
        )
        open(loconotion_path, "w").write(content)
        print(f"✓ Fixed notion-frame/scroller in {LOCONOTION_CSS}")
    else:
        print(f"WARNING: Could not find .notion-frame block in {LOCONOTION_CSS}")
else:
    print(f"WARNING: {LOCONOTION_CSS} not found — skipping loconotion custom CSS fix.")

print("\nDone. Reload your page.")
