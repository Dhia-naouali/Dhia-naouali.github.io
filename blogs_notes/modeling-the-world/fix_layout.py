#!/usr/bin/env python3
"""
fix_layout.py - Fixes layout issues in loconotion-generated HTML files.

Fixes:
  1. Content off-centered to the right (notion-frame is 1920px wide)
  2. Cover/banner image doesn't use full width
  3. Page title mis-aligned to the left
  4. Math equations (katex) left-aligned instead of centered

Usage:
  python fix_layout.py                  # fixes index.html in current directory
  python fix_layout.py path/to/file.html
"""

import re
import sys
import shutil
from pathlib import Path

# ── target file ──────────────────────────────────────────────────────────────
target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("index.html")
if not target.exists():
    print(f"ERROR: {target} not found.")
    sys.exit(1)

backup = target.with_suffix(".html.bak")
shutil.copy(target, backup)
print(f"Backup saved → {backup}")

html = target.read_text(encoding="utf-8")
original = html

# ── Fix 1: notion-frame width (1920px → 100%) ────────────────────────────────
# Notion sets width:1920px inline on the frame which pushes content off-screen
# when the sidebar isn't rendered. Replace with 100%.
html, n = re.subn(
    r'(class="notion-frame[^"]*"[^>]*style="[^"]*?)width:\s*\d+px',
    r'\1width: 100%',
    html
)
print(f"[1] notion-frame width fixed: {n} replacement(s)")

# ── Fix 2: notion-cursor-listener width (100vw → 100%) ───────────────────────
# 100vw includes the scrollbar width and can cause horizontal overflow.
html, n = re.subn(
    r'(class="notion-cursor-listener"[^>]*style="[^"]*?)width:\s*100vw',
    r'\1width: 100%',
    html
)
print(f"[2] cursor-listener width fixed: {n} replacement(s)")

# ── Fix 3: notion-frame height (viewport-locked → auto) ──────────────────────
# height: calc(-44px + 100vh) locks the frame to the viewport — kills scrolling.
html, n = re.subn(
    r'(class="notion-frame[^"]*"[^>]*style="[^"]*?)height:\s*calc\([^;]+\)',
    r'\1height: auto',
    html
)
print(f"[3] notion-frame height unlocked: {n} replacement(s)")

# Also fix max-height: 100% on notion-frame (prevents content from growing)
html, n = re.subn(
    r'(class="notion-frame[^"]*"[^>]*style="[^"]*?)max-height:\s*100%',
    r'\1max-height: none',
    html
)
print(f"[4] notion-frame max-height removed: {n} replacement(s)")

# ── Fix 5: Inject comprehensive CSS overrides ─────────────────────────────────
CSS_FIX = """<style id="loconotion-layout-fix">
/* ── Scrolling ── */
html, body {
  overflow: auto !important;
  overflow-x: hidden !important;
  height: auto !important;
}

/* ── Kill the 240px sidebar ghost offset ── */
.notion-sidebar,
.notion-sidebar-container,
[class*="notion-sidebar"] {
  display: none !important;
  width: 0 !important;
}

/* ── Main layout: full width, centered ── */
.notion-app-inner,
.notion-cursor-listener {
  width: 100% !important;
  max-width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

.notion-frame {
  width: 100% !important;
  max-width: 100% !important;
  height: auto !important;
  min-height: 100vh !important;
  max-height: none !important;
  overflow: visible !important;
}

/* ── Scroller: must overflow-y to allow scrolling ── */
.notion-scroller {
  overflow-y: auto !important;
  overflow-x: hidden !important;
  height: auto !important;
  min-height: 100vh !important;
  align-items: center !important;
}

/* ── Grid layout: missing grid-template-columns (normally set by Notion's JS) ── */
/* Without this, all .layout-content, .layout-full, cover, title collapse to left edge */
.layout {
  grid-template-columns: [full-start] 1fr [content-start] min(940px, 98%) [content-end] 1fr [full-end] !important;
}

/* ── Cover / banner: true full width ── */
.notion-page-cover-wrapper,
.notion-page-cover,
[class*="page-cover"] {
  width: 100% !important;
  max-width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  left: 0 !important;
  right: 0 !important;
}

.notion-page-cover img,
.notion-page-cover-wrapper img {
  width: 100% !important;
  object-fit: cover !important;
}

/* ── Page title: center it ── */
.notion-page-title,
.notion-title,
[class*="page-title"] {
  text-align: center !important;
  width: 100% !important;
  justify-content: center !important;
}

/* ── Content column: centered with readable max-width ── */
.notion-page-content {
  max-width: 940px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  width: 100% !important;
  padding-left: 32px !important;
  padding-right: 32px !important;
  box-sizing: border-box !important;
  font-size: 1.08em !important;
  line-height: 1.75 !important;
}

/* ── Math equations: centered ── */
.notion-equation-block {
  display: flex !important;
  justify-content: center !important;
  width: 100% !important;
}

.notion-equation-block > div,
.notion-equation-block .katex-display,
.katex-display {
  text-align: center !important;
  display: flex !important;
  justify-content: center !important;
  width: 100% !important;
}

.katex-display > .katex {
  text-align: center !important;
}

/* ── Images / figures: centered ── */
.notion-image-block,
.notion-asset-wrapper {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.notion-image-block img,
.notion-asset-wrapper img {
  display: block !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

/* ── Text selection: pseudoSelection--background is set to transparent in the static export ── */
.pseudoSelection ::selection,
::selection {
  background: #b4d5fe !important;
  color: inherit !important;
}
</style>
"""

# Inject before </head>
if "</head>" in html:
    html = html.replace("</head>", CSS_FIX + "</head>", 1)
    print("[5] CSS overrides injected before </head>")
else:
    # fallback: prepend to body
    html = html.replace("<body", CSS_FIX + "<body", 1)
    print("[5] CSS overrides injected before <body> (fallback)")

# ── Write output ──────────────────────────────────────────────────────────────
target.write_text(html, encoding="utf-8")

if html != original:
    print(f"\n✓ Done — {target} updated successfully.")
else:
    print(f"\n⚠ No changes were made — check selectors or HTML structure.")
