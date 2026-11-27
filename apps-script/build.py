#!/usr/bin/env python3
"""Build an Apps Script-ready Index.html from game-src.html.

Leaves hunter-gatherer.html (the GitHub Pages build) untouched. Run from anywhere:
    python3 apps-script/build.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "Index.html"

FULLSCREEN_CHECK = "if (!document.fullscreenEnabled && !document.webkitFullscreenEnabled) {"
FIRST_SCRIPT = "<script>\n/* ASSETS_PLACEHOLDER */"

# Safari and locked-down Chromebooks can block storage in third-party frames; fall back
# to in-memory settings so the sound/music toggles still work (they just reset each visit).
STORAGE_GUARD = """try { localStorage.getItem("x"); } catch (e) {
  const mem = {};
  Object.defineProperty(window, "localStorage", { value: {
    getItem: k => (k in mem ? mem[k] : null),
    setItem: (k, v) => { mem[k] = String(v); },
    removeItem: k => { delete mem[k]; }
  }});
}
"""

html = (ROOT / "game-src.html").read_text()

# Images and music are all data URIs in embedded.js, so nothing else needs inlining.
assert FIRST_SCRIPT in html, "first <script> with ASSETS_PLACEHOLDER not found"
html = html.replace(FIRST_SCRIPT, "<script>\n" + STORAGE_GUARD + "/* ASSETS_PLACEHOLDER */")
assets = (ROOT / "assets" / "embedded.js").read_text()
html = html.replace("/* ASSETS_PLACEHOLDER */", assets)

# The Sites/Apps Script iframes may not allow fullscreen; hide the button when blocked.
assert FULLSCREEN_CHECK in html, "fullscreen check not found"
html = html.replace(FULLSCREEN_CHECK, "if (document.fullscreenEnabled === false || !document.fullscreenEnabled && !document.webkitFullscreenEnabled) {")

assert not re.search(r'(src=|href=|url\()["\']?assets/', html), "a relative asset path is still referenced"
OUT.write_text(html)
print(f"Wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")
